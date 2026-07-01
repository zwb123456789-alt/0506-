"""
Enhanced OCS Feature Dataset for C2 Screening

Loads enhanced_ocs_features.npz and aligns with split manifests by record_id.
Supports per-fold, per-config training with train-only normalization.

Author: 1C-E31 C2 preparation
Date: 2026-06-25
"""

import json
import numpy as np
import torch
from torch.utils.data import Dataset
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class EnhancedOCSDataset(Dataset):
    """
    Dataset for enhanced OCS features.

    Loads one specific feature configuration (e.g., 'baseline_4dim', 'R_ratio_2d')
    and aligns with split manifest records by record_id.
    """

    def __init__(
        self,
        npz_path: Path,
        feature_config_name: str,
        split_records: List[Dict],
        normalize_params: Optional[Dict[str, np.ndarray]] = None,
        feature_definitions: Optional[Dict] = None
    ):
        """
        Args:
            npz_path: Path to enhanced_ocs_features.npz
            feature_config_name: Name of feature config (e.g., 'baseline_4dim')
            split_records: List of records from split manifest (train/val/test)
            normalize_params: {'mean': array, 'std': array} for normalization
            feature_definitions: Feature definitions dict (for validation)
        """
        self.npz_path = npz_path
        self.feature_config_name = feature_config_name
        self.split_records = split_records
        self.normalize_params = normalize_params
        self.feature_definitions = feature_definitions

        # Load npz
        self._load_npz()

        # Align split records with npz by record_id
        self._align_records()

        # Extract features and targets
        self._prepare_data()

    def _load_npz(self):
        """Load npz file and validate structure"""
        data = np.load(self.npz_path)
        self.npz_data = {key: data[key] for key in data.files}

        # Validate required fields
        assert 'record_ids' in self.npz_data, "npz missing 'record_ids'"
        assert self.feature_config_name in self.npz_data, \
            f"npz missing config '{self.feature_config_name}'"

        self.all_record_ids = self.npz_data['record_ids']

    def _align_records(self):
        """Align split records with npz by record_id"""
        # Build record_id -> npz_index mapping
        record_id_to_idx = {
            rid: i for i, rid in enumerate(self.all_record_ids)
        }

        # Extract indices for this split
        self.split_indices = []
        self.aligned_records = []

        for record in self.split_records:
            rid = record['record_id']

            if rid not in record_id_to_idx:
                raise ValueError(
                    f"record_id '{rid}' in split manifest but not in npz"
                )

            npz_idx = record_id_to_idx[rid]
            self.split_indices.append(npz_idx)
            self.aligned_records.append(record)

        self.split_indices = np.array(self.split_indices, dtype=np.int64)

        # Check for duplicates
        if len(self.split_indices) != len(np.unique(self.split_indices)):
            raise ValueError("Duplicate record_ids found in split")

    def _prepare_data(self):
        """Extract features and targets for this split"""
        # Extract features for this config
        full_features = self.npz_data[self.feature_config_name]
        self.X = full_features[self.split_indices].astype(np.float32)

        # Check for NaN/Inf
        if not np.all(np.isfinite(self.X)):
            raise ValueError(
                f"Non-finite values in {self.feature_config_name} features"
            )

        # Apply normalization if provided
        if self.normalize_params is not None:
            mean = self.normalize_params['mean']
            std = self.normalize_params['std']
            self.X = (self.X - mean) / (std + 1e-8)

        # Extract targets: yaw, pitch
        self.y = np.array([
            [rec['yaw_deg'], rec['pitch_deg']]
            for rec in self.aligned_records
        ], dtype=np.float32)

    def __len__(self) -> int:
        return len(self.aligned_records)

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor]:
        return torch.tensor(self.X[idx]), torch.tensor(self.y[idx])

    def get_feature_dim(self) -> int:
        """Return feature dimension"""
        return self.X.shape[1]


def compute_normalization_params(
    npz_path: Path,
    feature_config_name: str,
    train_records: List[Dict]
) -> Dict[str, np.ndarray]:
    """
    Compute mean/std from train split only.

    Args:
        npz_path: Path to enhanced_ocs_features.npz
        feature_config_name: Feature config name
        train_records: Train split records

    Returns:
        {'mean': array, 'std': array}
    """
    # Load npz
    data = np.load(npz_path)
    all_record_ids = data['record_ids']
    full_features = data[feature_config_name]

    # Build mapping
    record_id_to_idx = {rid: i for i, rid in enumerate(all_record_ids)}

    # Extract train indices
    train_indices = []
    for rec in train_records:
        rid = rec['record_id']
        if rid not in record_id_to_idx:
            raise ValueError(f"Train record_id '{rid}' not in npz")
        train_indices.append(record_id_to_idx[rid])

    train_indices = np.array(train_indices, dtype=np.int64)

    # Extract train features
    train_features = full_features[train_indices].astype(np.float32)

    # Compute stats
    mean = train_features.mean(axis=0)
    std = train_features.std(axis=0)

    return {'mean': mean, 'std': std}


def load_feature_definitions(definitions_path: Path) -> Dict:
    """Load feature_definitions.json"""
    with open(definitions_path, encoding='utf-8') as f:
        return json.load(f)


def get_c2_participant_configs(feature_definitions: Dict) -> List[Dict]:
    """
    Extract configs with c2_participant=True.

    Returns:
        List of config dicts, sorted by config_id
    """
    configs = feature_definitions['configs']
    c2_configs = [cfg for cfg in configs if cfg.get('c2_participant', False)]
    c2_configs.sort(key=lambda x: x['config_id'])
    return c2_configs


def validate_npz_structure(
    npz_path: Path,
    feature_definitions: Dict
) -> Dict[str, any]:
    """
    Validate npz structure against feature_definitions.

    Returns:
        Validation report dict
    """
    data = np.load(npz_path)

    report = {
        'npz_path': str(npz_path),
        'npz_keys': list(data.files),
        'n_records': len(data['record_ids']) if 'record_ids' in data else 0,
        'missing_configs': [],
        'config_shapes': {},
        'issues': []
    }

    # Check record_ids
    if 'record_ids' not in data:
        report['issues'].append("Missing 'record_ids' in npz")
        return report

    n_records = len(data['record_ids'])

    # Check each config
    for cfg in feature_definitions['configs']:
        config_name = cfg['config_name']
        expected_dim = cfg['dim']

        if config_name not in data:
            report['missing_configs'].append(config_name)
            continue

        feature_array = data[config_name]
        actual_shape = feature_array.shape
        expected_shape = (n_records, expected_dim)

        report['config_shapes'][config_name] = {
            'actual': actual_shape,
            'expected': expected_shape,
            'match': actual_shape == expected_shape
        }

        if actual_shape != expected_shape:
            report['issues'].append(
                f"{config_name}: shape {actual_shape} != {expected_shape}"
            )

    return report


if __name__ == '__main__':
    """Self-test: validate npz structure and alignment"""

    # Paths
    ROOT = Path(__file__).resolve().parents[2]
    NPZ_PATH = ROOT / "v0.4_results/04_ocs_features/enhanced_ocs_features.npz"
    DEFINITIONS_PATH = ROOT / "v0.4_results/04_ocs_features/feature_definitions.json"
    SPLIT_PATH = ROOT / "v0.4_results/03_training_baseline/e25_multifold_yawblock/split_manifest_circ_yawblock_fold0.json"

    print("=== Enhanced OCS Dataset Self-Test ===\n")

    # Load definitions
    print("Loading feature definitions...")
    feature_defs = load_feature_definitions(DEFINITIONS_PATH)
    c2_configs = get_c2_participant_configs(feature_defs)
    print(f"  Found {len(c2_configs)} C2 participant configs")

    # Validate npz structure
    print("\nValidating npz structure...")
    val_report = validate_npz_structure(NPZ_PATH, feature_defs)
    print(f"  NPZ contains {val_report['n_records']} records")
    print(f"  NPZ has {len(val_report['npz_keys'])} keys")

    if val_report['issues']:
        print("  ISSUES:")
        for issue in val_report['issues']:
            print(f"    - {issue}")
    else:
        print("  [OK] All configs present with correct shapes")

    # Load split manifest
    print("\nLoading split manifest (fold 0)...")
    with open(SPLIT_PATH, encoding='utf-8') as f:
        split_manifest = json.load(f)

    train_records = split_manifest['train']
    val_records = split_manifest['val']
    test_records = split_manifest['test']
    print(f"  Train: {len(train_records)}, Val: {len(val_records)}, Test: {len(test_records)}")

    # Test alignment for one config
    test_config = c2_configs[0]
    config_name = test_config['config_name']
    print(f"\nTesting alignment for '{config_name}'...")

    # Compute normalization params
    norm_params = compute_normalization_params(NPZ_PATH, config_name, train_records)
    print(f"  Train mean shape: {norm_params['mean'].shape}")
    print(f"  Train std shape: {norm_params['std'].shape}")

    # Create datasets
    train_dataset = EnhancedOCSDataset(
        NPZ_PATH, config_name, train_records, norm_params, feature_defs
    )
    val_dataset = EnhancedOCSDataset(
        NPZ_PATH, config_name, val_records, norm_params, feature_defs
    )
    test_dataset = EnhancedOCSDataset(
        NPZ_PATH, config_name, test_records, norm_params, feature_defs
    )

    print(f"  Train dataset: {len(train_dataset)} samples, feature_dim={train_dataset.get_feature_dim()}")
    print(f"  Val dataset: {len(val_dataset)} samples, feature_dim={val_dataset.get_feature_dim()}")
    print(f"  Test dataset: {len(test_dataset)} samples, feature_dim={test_dataset.get_feature_dim()}")

    # Test batch loading
    print("\nTesting batch loading...")
    X_sample, y_sample = train_dataset[0]
    print(f"  X shape: {X_sample.shape}, y shape: {y_sample.shape}")
    print(f"  X dtype: {X_sample.dtype}, y dtype: {y_sample.dtype}")
    print(f"  X finite: {torch.isfinite(X_sample).all()}, y finite: {torch.isfinite(y_sample).all()}")

    print("\n=== Self-Test Complete ===")

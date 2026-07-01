"""
C2 Screening Output Schema Definitions

Defines JSON schemas for C2 OCS-only screening results.

Author: 1C-E31 C2 preparation
Date: 2026-06-25
"""

from typing import Dict, List, Optional
from pathlib import Path


# ══════════════════════════════════════════════════════════
# Per-Config, Per-Fold Result Schema
# ══════════════════════════════════════════════════════════

PER_CONFIG_FOLD_SCHEMA = {
    "type": "object",
    "required": [
        "task", "config_name", "fold_id", "config_id", "claim_class",
        "feature_keys", "feature_dim", "training_protocol", "split_info",
        "normalization_params", "model_info", "training_summary",
        "final_metrics", "timestamp"
    ],
    "properties": {
        "task": {"type": "string"},
        "config_name": {"type": "string"},
        "fold_id": {"type": "integer"},
        "config_id": {"type": "integer"},
        "claim_class": {"type": "string"},
        "feature_keys": {"type": "array", "items": {"type": "string"}},
        "feature_dim": {"type": "integer"},

        "training_protocol": {
            "type": "object",
            "required": ["model_type", "hidden_dim", "n_layers", "max_epochs", "lr", "seed"],
            "properties": {
                "model_type": {"type": "string"},
                "hidden_dim": {"type": "integer"},
                "n_layers": {"type": "integer"},
                "max_epochs": {"type": "integer"},
                "lr": {"type": "number"},
                "batch_size": {"type": "integer"},
                "optimizer": {"type": "string"},
                "seed": {"type": "integer"},
            }
        },

        "split_info": {
            "type": "object",
            "required": ["split_manifest_path", "n_train", "n_val", "n_test"],
            "properties": {
                "split_manifest_path": {"type": "string"},
                "split_method": {"type": "string"},
                "n_train": {"type": "integer"},
                "n_val": {"type": "integer"},
                "n_test": {"type": "integer"},
            }
        },

        "normalization_params": {
            "type": "object",
            "required": ["computed_from", "mean", "std"],
            "properties": {
                "computed_from": {"type": "string"},
                "mean": {"type": "array", "items": {"type": "number"}},
                "std": {"type": "array", "items": {"type": "number"}},
            }
        },

        "model_info": {
            "type": "object",
            "required": ["n_params", "checkpoint_path"],
            "properties": {
                "n_params": {"type": "integer"},
                "checkpoint_path": {"type": "string"},
                "checkpoint_size_mb": {"type": "number"},
            }
        },

        "training_summary": {
            "type": "object",
            "required": ["best_epoch", "best_val_avg_acc", "elapsed_s"],
            "properties": {
                "best_epoch": {"type": "integer"},
                "best_val_avg_acc": {"type": "number"},
                "final_train_loss": {"type": "number"},
                "elapsed_s": {"type": "number"},
                "warnings": {"type": "array", "items": {"type": "string"}},
            }
        },

        "final_metrics": {
            "type": "object",
            "required": ["val", "test"],
            "properties": {
                "val": {
                    "type": "object",
                    "required": [
                        "loss", "yaw_acc", "pitch_acc",
                        "yaw_circular_mae_deg", "pitch_mae_deg",
                        "yaw_correct_count", "pitch_correct_count",
                        "yaw_within_1_bin_rate", "yaw_within_3_bins_rate", "yaw_within_5_bins_rate",
                        "pitch_within_1_bin_rate", "pitch_within_3_bins_rate", "pitch_within_5_bins_rate"
                    ],
                },
                "test": {
                    "type": "object",
                    "required": [
                        "loss", "yaw_acc", "pitch_acc",
                        "yaw_circular_mae_deg", "pitch_mae_deg",
                        "yaw_correct_count", "pitch_correct_count",
                        "yaw_within_1_bin_rate", "yaw_within_3_bins_rate", "yaw_within_5_bins_rate",
                        "pitch_within_1_bin_rate", "pitch_within_3_bins_rate", "pitch_within_5_bins_rate"
                    ],
                },
            }
        },

        "timestamp": {"type": "string"},
    }
}


# ══════════════════════════════════════════════════════════
# C2 Screening Summary Schema
# ══════════════════════════════════════════════════════════

C2_SCREENING_SUMMARY_SCHEMA = {
    "type": "object",
    "required": [
        "task", "execution_date", "protocol", "n_configs", "n_folds",
        "feature_source", "training_protocol_template", "results_summary",
        "output_structure"
    ],
    "properties": {
        "task": {"type": "string"},
        "execution_date": {"type": "string"},
        "protocol": {"type": "string"},

        "n_configs": {"type": "integer"},
        "n_folds": {"type": "integer"},

        "feature_source": {
            "type": "object",
            "required": ["npz_path", "definitions_path", "n_records"],
            "properties": {
                "npz_path": {"type": "string"},
                "definitions_path": {"type": "string"},
                "summary_path": {"type": "string"},
                "n_records": {"type": "integer"},
            }
        },

        "training_protocol_template": {
            "type": "object",
            "required": ["model_type", "hidden_dim", "n_layers", "max_epochs", "lr"],
            "properties": {
                "model_type": {"type": "string"},
                "hidden_dim": {"type": "integer"},
                "n_layers": {"type": "integer"},
                "max_epochs": {"type": "integer"},
                "lr": {"type": "number"},
                "batch_size": {"type": "integer"},
                "optimizer": {"type": "string"},
            }
        },

        "results_summary": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["config_name", "config_id", "claim_class", "feature_dim", "fold_results"],
                "properties": {
                    "config_name": {"type": "string"},
                    "config_id": {"type": "integer"},
                    "claim_class": {"type": "string"},
                    "feature_dim": {"type": "integer"},
                    "feature_keys": {"type": "array", "items": {"type": "string"}},

                    "fold_results": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "required": ["fold_id", "result_path", "best_val_avg_acc"],
                            "properties": {
                                "fold_id": {"type": "integer"},
                                "result_path": {"type": "string"},
                                "best_val_avg_acc": {"type": "number"},
                                "test_yaw_acc": {"type": "number"},
                                "test_pitch_acc": {"type": "number"},
                            }
                        }
                    },

                    "aggregate_metrics": {
                        "type": "object",
                        "properties": {
                            # Val metrics
                            "mean_val_avg_acc": {"type": "number"},
                            "std_val_avg_acc": {"type": "number"},

                            # Test accuracy
                            "mean_test_yaw_acc": {"type": "number"},
                            "std_test_yaw_acc": {"type": "number"},
                            "mean_test_pitch_acc": {"type": "number"},
                            "std_test_pitch_acc": {"type": "number"},

                            # Test MAE
                            "mean_test_yaw_circular_mae_deg": {"type": "number"},
                            "std_test_yaw_circular_mae_deg": {"type": "number"},

                            # Test within-k rates (yaw)
                            "mean_test_yaw_within_1_bin_rate": {"type": "number"},
                            "std_test_yaw_within_1_bin_rate": {"type": "number"},
                            "mean_test_yaw_within_3_bins_rate": {"type": "number"},
                            "std_test_yaw_within_3_bins_rate": {"type": "number"},
                            "mean_test_yaw_within_5_bins_rate": {"type": "number"},
                            "std_test_yaw_within_5_bins_rate": {"type": "number"},

                            # Test correct counts
                            "mean_test_yaw_correct_count": {"type": "number"},
                            "std_test_yaw_correct_count": {"type": "number"},
                            "mean_test_pitch_correct_count": {"type": "number"},
                            "std_test_pitch_correct_count": {"type": "number"},

                            # Test within-k rates (pitch)
                            "mean_test_pitch_within_1_bin_rate": {"type": "number"},
                            "std_test_pitch_within_1_bin_rate": {"type": "number"},
                            "mean_test_pitch_within_3_bins_rate": {"type": "number"},
                            "std_test_pitch_within_3_bins_rate": {"type": "number"},
                            "mean_test_pitch_within_5_bins_rate": {"type": "number"},
                            "std_test_pitch_within_5_bins_rate": {"type": "number"},
                        }
                    }
                }
            }
        },

        "output_structure": {
            "type": "object",
            "required": ["base_dir", "per_config_folders"],
            "properties": {
                "base_dir": {"type": "string"},
                "per_config_folders": {"type": "array", "items": {"type": "string"}},
            }
        },

        "exclusions": {
            "type": "object",
            "properties": {
                "excluded_configs": {"type": "array", "items": {"type": "string"}},
                "exclusion_reason": {"type": "string"},
            }
        }
    }
}


# ══════════════════════════════════════════════════════════
# Helper: Generate per-config result template
# ══════════════════════════════════════════════════════════

def generate_per_config_result_template(
    config: Dict,
    fold_id: int,
    split_manifest_path: str,
    n_train: int,
    n_val: int,
    n_test: int,
    training_protocol: Dict,
) -> Dict:
    """
    Generate template for per-config, per-fold result JSON.

    To be filled in after training with actual metrics, model info, etc.
    """
    template = {
        "task": "1C-E32 C2 OCS-only screening",
        "config_name": config['config_name'],
        "fold_id": fold_id,
        "config_id": config['config_id'],
        "claim_class": config['claim_class'],
        "feature_keys": config['feature_keys'],
        "feature_dim": config['dim'],

        "training_protocol": training_protocol,

        "split_info": {
            "split_manifest_path": split_manifest_path,
            "split_method": "circ_yaw_block",
            "n_train": n_train,
            "n_val": n_val,
            "n_test": n_test,
        },

        "normalization_params": {
            "computed_from": "train_split_only",
            "mean": None,  # To be filled
            "std": None,   # To be filled
        },

        "model_info": {
            "n_params": None,  # To be filled
            "checkpoint_path": None,  # To be filled
            "checkpoint_size_mb": None,  # To be filled
        },

        "training_summary": {
            "best_epoch": None,  # To be filled
            "best_val_avg_acc": None,  # To be filled
            "final_train_loss": None,  # To be filled
            "elapsed_s": None,  # To be filled
            "warnings": [],
        },

        "final_metrics": {
            "val": None,  # To be filled
            "test": None,  # To be filled
        },

        "timestamp": None,  # To be filled
    }

    return template


# ══════════════════════════════════════════════════════════
# Helper: Generate C2 summary template
# ══════════════════════════════════════════════════════════

def generate_c2_summary_template(
    c2_configs: List[Dict],
    n_folds: int,
    feature_source_info: Dict,
    training_protocol: Dict,
    output_base_dir: Path,
) -> Dict:
    """
    Generate template for C2 screening summary JSON.
    """
    template = {
        "task": "1C-E32 C2 OCS-only screening",
        "execution_date": None,  # To be filled
        "protocol": "fixed_protocol_no_hyperparam_search",

        "n_configs": len(c2_configs),
        "n_folds": n_folds,

        "feature_source": feature_source_info,

        "training_protocol_template": training_protocol,

        "results_summary": [],  # To be filled with per-config summaries

        "output_structure": {
            "base_dir": str(output_base_dir),
            "per_config_folders": [
                str(output_base_dir / cfg['config_name'])
                for cfg in c2_configs
            ],
        },

        "exclusions": {
            "excluded_configs": ["constant_check_1d"],
            "exclusion_reason": "constant sanity check, not for C2 evaluation",
        }
    }

    return template


if __name__ == '__main__':
    """Self-test: print schemas"""
    import json

    print("=== C2 Screening Schema Self-Test ===\n")

    print("Per-Config Fold Schema Keys:")
    print(f"  Required: {PER_CONFIG_FOLD_SCHEMA['required']}")

    print("\nC2 Screening Summary Schema Keys:")
    print(f"  Required: {C2_SCREENING_SUMMARY_SCHEMA['required']}")

    print("\n=== Self-Test Complete ===")

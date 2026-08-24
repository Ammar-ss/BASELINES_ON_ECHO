# Known issues in the EchoJEPA eval code

Read this before trusting any number in results/.

## 1. Logged MAE is scaled by target_std

eval.py line ~671 multiplies MAE by target_std to convert back to real units, but the dataloader (line ~637) never normalizes the labels. Every logged value is therefore the true MAE times target_std.

Divide before reporting. The divisor differs per cell.

| Cell | target_std |
|---|---|
| EchoNet-Dynamic / EF | 12.4072 |
| EchoNet-LVH / LVIDd | 0.8335 |
| MIMIC / LVEDD | 0.7892 |
| MIMIC / RVSP | 11.7233 |

The prediction CSV writer has the same problem: it applies `(val * std) + mean` to values that were never normalized. Undo with `(x - mean) / std` before plotting. analysis/plot_scatter.py already does this.

## 2. --debugmode needs an explicit value

Declared `type=bool` rather than `action="store_true"`, so `--debugmode` alone errors. Use `--debugmode True`.

## 3. DDP prefix mismatch on inference

Checkpoints saved on multi-GPU have `module.`-prefixed keys, so single-GPU loading fails with "Missing key(s)". Fixed by inserting one line above the load_state_dict call in evals/video_classification_frozen/eval.py, around line 780:

    pretrained_dict = [{k.replace("module.", "", 1): v for k, v in pd.items()} for pd in pretrained_dict]

This is the only modification made to the engine. The original is backed up as eval.py.bak.

## 4. Only rank 0 writes predictions

Each rank sees 1/N of the eval set and only rank 0 writes to the CSV. Run inference single-GPU to get the full test set. Always record the actual n.

## 5. iterations per epoch is per-rank

ipe = len(train_loader) after DistributedSampler splits the data. 7465 samples on 4 GPUs gives 1867. Not a bug.

## 6. nodes and tasks_per_node in configs are ignored

World size comes from len(args.devices) on the command line, evals/main.py line 109.

## 7. Their echonet-dynamic configs point at Toronto data

configs/eval/vitg-384/lvef/echonet-dynamic/*.yaml are tagged "...echonet-dynamic..." but dataset_train points at a4c_b_lvef_train_224px.csv, their internal set. The tags were updated and the paths were not.

The target_mean and target_std in them are EchoNet's, 55.7776 and 12.4064, matching our own computation of 55.7776 and 12.4072. The difference is ddof only.

## 8. Published numbers may be validation rather than test

Our val and test differ meaningfully. PanEcho EF: val 5.094, test 5.283. The published 5.10 matches our val far more closely than our test. Both are reported separately throughout.

## 9. Resolution

All configs use 112, which both wrappers upscale to 224 internally. EchoNet-Dynamic is natively 112 so nothing is lost. EchoNet-LVH is 1024x768 and MIMIC is 1016x708, so both are downscaled then upscaled and are likely understated.

Keeping 112 everywhere is deliberate. It makes PanEcho and EchoPrime directly comparable, since both then run decode to 112 to upscale to 224.

## 10. EchoPrime is run in a degenerate mode

EchoPrime is a multi-video, view-informed model with MIL attention across views. Every cell here feeds one clip per study through VideoDataset, so that machinery is switched off. Any EchoPrime result reflects the encoder, not the architecture.

VideoGroupDataset exists in the repo for the multi-video case and is the correct setup for testing EchoPrime as designed. Not yet used.

## 11. Embedding dimensions differ

PanEcho outputs 768, EchoPrime outputs 512. The probe adapts, but the two rows do not have identical probe capacity.

## 12. MIMIC clip selection

One random clip per study, seed 0, drawn from a median of 41. For LVEDD this adds noise. For RVSP it may invalidate the experiment entirely, since RVSP requires the tricuspid regurgitation trace on spectral Doppler and the odds of drawing it are roughly 1 in 41.

## 13. Single run per cell

No seed variance anywhere. Differences under a few percent should not be treated as real.

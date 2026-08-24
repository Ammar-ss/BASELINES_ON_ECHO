# Echo Foundation Model Benchmark

Three echocardiography foundation models evaluated across three datasets and four targets. The backbone stays frozen in every run and only a small probe is trained on top, following the protocol from the EchoJEPA paper so the numbers can be lined up against theirs.

## The question

A foundation model gets trained on one distribution and then evaluated on whatever tasks its authors picked. What I wanted to find out is how well the representation holds up when you change the view, change the measurement, or change the hospital.

## Results

Test MAE in the units of each target.

| | EchoNet-Dynamic, EF (%) | EchoNet-LVH, LVIDd (cm) | MIMIC, LVEDD (cm) | MIMIC, RVSP (mmHg) |
|---|---|---|---|---|
| PanEcho | 5.39 | 0.451 | 0.590 | 8.30 |
| EchoPrime | 5.08 | 0.458 | 0.557 | not run |
| EchoJEPA-L | 5.26 | 0.411 | contaminated | contaminated |
| PanEcho zero-shot | 6.45 | 0.452 | 0.585 | 8.76 |

EchoJEPA-L was pretrained on MIMIC-IV-Echo, so running it there would just be testing on its own training data. Those two cells are left empty on purpose.

Zero-shot means PanEcho's own supervised head read straight out, with no probe and no training. EchoPrime and EchoJEPA do not have task heads, so there is no zero-shot row for either of them.

Everything else including R squared, bias and validation numbers is in results/TABLES.md, and the per cell write up is in results/RESULTS.md.

## Does the pipeline actually work

| Model | My validation | My test | Published |
|---|---|---|---|
| PanEcho | 5.094 | 5.393 | 5.10 |
| EchoPrime | 5.066 | 5.077 | 4.87 |
| EchoJEPA-L | 4.928 | 5.259 | 5.76 |

All on EchoNet-Dynamic LVEF. Each model lands close to its published number and EchoJEPA-L actually comes in better than published on validation. This is the only cell in the whole benchmark with an external reference to check against, so it is what makes the rest of the numbers worth reading.

## What the numbers say

If you threw away the image and just predicted the dataset average for every patient, you would get an MAE of 9.09 on EF, 0.554 on LVIDd, 0.610 on LVEDD and 8.85 on RVSP. Against that, every model is 40 to 44 percent better on EchoNet-Dynamic. On MIMIC LVEDD, PanEcho is 3 percent better and EchoPrime is 9 percent. On MIMIC RVSP, zero-shot manages 1 percent.

The same measurement does not carry over between hospitals nearly as well as I expected. LVIDd goes from 0.451 cm on EchoNet-LVH to 0.590 cm on MIMIC, and the label distributions are almost the same in both, 4.705 plus or minus 0.834 against 4.560 plus or minus 0.789. Three things changed at once though, no view filtering, one random clip per study instead of a curated video, and two and a half times less training data, so I cannot pin it on any one of them.

PanEcho's trained probe beats its own supervised head by 18 percent on EF, but on both LVIDd cells it adds essentially nothing.

RVSP fails for everything I tried. R squared sits at or below zero, meaning the predictions do worse than the dataset average. There is a confound I could not resolve, which is that RVSP gets measured off a spectral Doppler trace and these runs feed one random clip out of roughly forty per study, so the model may simply never have been shown the right image.

I also looked at how much the predictions vary compared to how much the labels vary. On EchoNet-Dynamic the predictions cover about 80 percent of the true range. On MIMIC RVSP, PanEcho covers 16 percent of it, so the model is putting out something close to a constant while still landing in a believable range. MAE on its own does not catch that.

## An extra check on repeat clips

Separately from the benchmark I pulled 150 MIMIC studies that had at least six apical four chamber clips each, and ran PanEcho on every clip.

| Target | SD within a study | SD between studies |
|---|---|---|
| EF | 3.44 | 5.19 |
| LVEDV | 14.31 | 17.69 |
| LVESV | 8.23 | 12.11 |
| LVIDd | 0.17 | 0.21 |
| LVIDs | 0.19 | 0.27 |

Six clips, same view, same patient, same sitting. The EF prediction shifts by 3.44 points depending on which one you feed it. That is two thirds of the spread you see across completely different patients, and it is about the same size as the model's total error. Every benchmark here, mine included, uses one clip per study and reports the result as if it were a property of the model.

## Layout

```
configs/       one YAML per cell, named model_dataset_target
data_prep/     turns each dataset into the two column CSV the engine reads
scripts/       run.sh, status.sh, kill.sh, collect.sh
analysis/      zeroshot.py, plot_scatter.py, plot_curve.py, compute_metrics.py
notes/         known_issues.md, worth reading before trusting any number
results/       RESULTS.md, TABLES.md, metrics.csv, epoch logs, figures, curves
paths.sh       every machine specific path in one file
```

Checkpoints are not here, they are two gigabytes each and live on the server. Per patient prediction files and raw run logs are also left out because they contain MIMIC data, which is credentialed. Everything needed to check or replot a number is in results/metrics.csv and results/epoch_logs.

The eval engine is a fork of bowang-lab/EchoJEPA with a single line changed, which is explained in notes/known_issues.md.

## Running something

```bash
source paths.sh
./scripts/run.sh                        # lists the configs
./scripts/run.sh panecho_lvh_lvidd 6    # launches on six free GPUs
./scripts/status.sh panecho_lvh_lvidd   # checks progress
./scripts/collect.sh                    # pulls artefacts into results/
```

## Before you read any number

The eval code multiplies MAE by target_std before logging it, but the dataloader never normalises the labels in the first place, so every logged value comes out inflated by that factor. The divisor is different for each cell. Everything sitting in results/ has already been divided. Details are in notes/known_issues.md.

## Models

PanEcho is a ConvNeXt-Tiny run per frame with a four layer transformer on top, 42M parameters, trained supervised on 39 clinical outputs. EchoPrime is MViT-v2-S, 35M parameters, trained contrastively on video and report pairs. EchoJEPA-L is a ViT-Large, 300M parameters, trained self supervised on MIMIC-IV-Echo.

All three are cloned from their upstream repositories and are not committed here.

## Limitations

Single run per cell and no seed variance, so differences under a few percent should not be taken as real.

Every config uses resolution 112 so that all three models see an identical pipeline. EchoNet-Dynamic is natively 112 so nothing is lost there, but EchoNet-LVH is 1024 by 768 and MIMIC is 1016 by 708, and both get downscaled and then upscaled again by the wrapper. Those two are probably understated.

MIMIC had no view filtering in these runs. Per clip view labels for all 525,141 files only turned up afterwards.

EchoPrime is designed as a multi video model with attention across the views in a study, and here it only ever sees one clip at a time. So its numbers reflect the encoder rather than the full architecture.

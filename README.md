# ChronoGauge ensemble for cross-species analyses (using _Arabidopsis thaliana_ in training data)
### Work assocaciated with:
## Machine learning models reveal environmental and genetic factors associated with the plant circadian clock
Connor Reynolds<sub>1</sub>, Joshua Colmer<sub>1</sub>, Hannah Rees<sub>2</sub>, Ehsan Khajouei<sub>1</sub>, Rachel Rusholme-Pilcher<sub>1</sub>, Hiroshi Kudoh<sub>3</sub>, Antony Dodd<sub>4</sub>, Anthony Hall<sub>1,5</sub>

<sub>1</sub>Earlham Institute, Norwich Research Park  
<sub>2</sub>Institue of Biological, Environmental & Rural Sciences (IBERS)  
<sub>3</sub>Centre for Ecological Research, Kyoto University  
<sub>4</sub>John Innes Centre, Norwich Research Park  
<sub>5</sub>School of Biological Sciences, University of East Anglia  

DOI: [10.1101/2024.10.28.620591](https://www.biorxiv.org/content/10.1101/2024.10.28.620591v1)

## Overview
This repository in an extention of [ChronoGauge](https://github.com/ConnorReynoldsUK/ChronoGauge) and includes work related specifically to the application of our ensemble models (trained using _A. thaliana_ expression) to non-model species for circadian time (CT) prediction.

We preface by stating that applying ChronoGauge across different species (after training exclusively in _A. thaliana_) is not expected to give as reliable predicted compared with training & testing on the same species. We also note that it is required that non-model species include samples from least 2 time-points that were harvested ~12 hours apart.
 

## Installation
This repository requires an identical environment to the original ChronoGauge repository.

A working environment for running ChronoGauge can be installed via Anaconda. Details on installing an Anaconda distribution can be found [here](https://www.anaconda.com/download/).

### For MacOS/Linux users
In the command terminal:
```
git clone https://github.com/ConnorReynoldsUK/ChronoGauge
cd ChronoGauge_
source install_current.sh
```

The environment installation should take ~2 minutes.

**Note:** The original script in our paper uses a conda environment installed specifically in AlmaLinux 5.14.0 OS on the HPC, which is not reproducible across other OS. We provide 'env/chronogauge_original.yml' which can be used to install the environment in the respective OS using:

```
conda env create PATH_TO_REPO/ChronoGauge/env/chronogauge_alma.yml -n chronogauge_alma
conda activate chronogauge_alma
```

## Ortholog mapping
Since gene features do not correspond across species, it is required to identify and select genes in the test species which are orthologous to gene features used by the training species. The script `map_orthologs.py` can be used for this mapping. For example, _A. thaliana_ is used as a training species and wheat is used as a test species:

```
python3 map_orthologs.py  --species_name wheat --ortholog_list data/ortholog_lists/wheat_ortholog_list.csv --x_test data/original_exp_matrices/original_wheat_exp.csv --target_test data/targets/target_wheat.csv
```

The ortholog gene mapper takes:
1. A .csv file with test species genes in column 0 and the training species orthologs in column 2 (e.g. orthologous genes between _A. thaliana_ and wheat `data/ortholog_lists_wheat_ortholog_lists.csv`)
2. An expression matrix for a test species that is different from the species using in training (e.g. wheat expression matrix `data/original_exp_matrices/original_wheat_exp.csv`)
3. OPTIONAL a .csv file containing the sampling times for the test species (e.g. `data/targets/target_wheat.csv`)


This script will identify and map genes from the non-model species to orthologous A. thaliana genes. Where multiple non-model species genes map to a single A. thaliana gene, we take the average of their expression. The output is a gene expression matrix for the non-model species with all genes being replace by A. thaliana orthologs.

## Model training and testing across species
To train and test models across species with a specified feature sets, we provide the script `train_model_xspecies.py`. By default, the script will train a model using 17 cannonical circadain clock genes as features.

For example, the script can be run using the following command to train a model in _A. thaliana_ and test it in wheat using a model ID of 0:

```
python3 train_model_xspecies.py --x_test data/ortholog_exp_matrices/X_wheat_orth.csv --target_test data/targets/target_wheat.csv --experiment_name wheat --model_id 0
```
Where the parameter `--x_test` requires an expression matrix of the test species with ortholog genes mapped and replaced with _A. thaliana_, as described previously.


Multiple models each with a unique ID value can be trained and tested using the following command:

```
for i in {0..10}; 
do python train_model_xspecies.py --xtest data/ortholog_exp_matrices/X_wheat_orth.csv --target_test data/targets/target_wheat.csv --experiment_name wheat --model_id $1
done
```
Each script should take ~ 1 minute to complete. To analyze the results of multiple models as an ensemble, we refer to the [Jupyter notebook for ensemble aggregation](https://github.com/ConnorReynoldsUK/ChronoGauge/blob/main/notebooks/example_ensemble_aggregation.ipynb) found within the original ChronoGauge repository.

## Datasets
The following datasets are included in this repository:
* Training _A. thaliana_ data (_N_ samples = 56) includes experiments from _Cortijo et al._[1], _Yang et al._[2] and _Romanowski et al._[3].
* _Glycine max_ (soybean) expression data from circadian experiment by _Li et al._[4]
* _Brassica rapa_ expression data from circadian experiment by _Greenham et al._[5]
* _Arabidopsis halleri_ expression data from wild samples by _Nagano et al._[6] and _Honjo et al._[7]
* _Triticum aestivum_ (wheat) expression data from circadian experiment by _Rees et al.[8]


## References
1. Cortijo, S., Aydin, Z., Ahnert, S. & Locke, J. C. Widespread inter‐individual gene expression variability in Arabidopsis thaliana. Mol. Syst. Biol. 15, e8591 (2019).
2. Yang, Y., Li, Y., Sancar, A. & Oztas, O. The circadian clock shapes the Arabidopsis transcriptome by regulating alternative splicing and alternative polyadenylation. J. Biol. Chem. 295, 7608 (2020).
3. Romanowski, A., Schlaen, R. G., Perez-Santangelo, S., Mancini, E. & Yanovsky, M. J. Global transcriptome analysis reveals circadian control of splicing events in Arabidopsis thaliana. Plant J. 103, 889–902 (2020).
4. Li, M., Cao, L., Mwimba, M., Zhou, Y., Li, L., Zhou, M., Schnable, P. S., O’Rourke, J. A., Dong, X. & Wang, W. Comprehensive mapping of abiotic stress inputs into the soybean circadian clock. Proc. Natl. Acad. Sci. 116, 23840–23849 (2019).
5. Greenham, K., Sartor, R. C., Zorich, S., Lou, P., Mockler, T. C. & McClung, C. R. Expansion of the circadian transcriptome in Brassica rapa and genome-wide diversification of paralog expression patterns. eLife 9, e58993 (2020).
6. Nagano, A. J., Kawagoe, T., Sugisaka, J., Honjo, M. N., Iwayama, K. & Kudoh, H. Annual transcriptome dynamics in natural environments reveals plant seasonal adaptation. Nat. Plants 5, 74–83 (2019).
7. Honjo, M. N., Emura, N., Kawagoe, T., Sugisaka, J., Kamitani, M., Nagano, A. J. & Kudoh, H. Seasonality of interactions between a plant virus and its host during persistent infection in a natural environment. ISME J. 14, 506–518 (2020).
8. Rees, H., Joynson, R., Brown, J. K. M. & Hall, A. Naturally occurring circadian rhythm variation associated with clock gene loci in Swedish Arabidopsis accessions. Plant Cell Environ. 44, 807–820 (2021).

import sys
import pandas as pd
import numpy as np
import random
import os
import argparse


#make sure same seed is used throughout
SEED = 0
random.seed(SEED)
np.random.seed(SEED)
os.environ['PYTHONHASHSEED'] = str(SEED)






parser = argparse.ArgumentParser(description='An example script which maps orthologs from the training species (here Arabidopis thaliana) to that of the test data.\nGenerates a new expression matrix for the test data, using gene IDs for the training data.')
parser.add_argument('--ortholog_list', type=str, help='Define the ortholog matrix with the non-model species for testing (column 0) and the model species (A. thaliana, column 1). Default is Arabodpsis helleri orthologs', default='data/ortholog_lists/helleri_ortholog_list.csv')
parser.add_argument('--x_test', type=str, help='Define the test expression matrix .csv file that we will map ortholgs to. Default will be A. helleri expression.', default='data/original_exp_matrices/original_helleri_exp.csv')
parser.add_argument('--target_test', type=str, help='Sampling times in hours for test data across 1st column of .csv file to label expression matrix.\nIf None, will keep labels from original expression matrix.')
parser.add_argument('--out_results', type=str, help='Directory to output test results in .csv format.', default='results/example_ortholog_exp')
parser.add_argument('--species_name', type=str, help='Name of the non-model species to be added as a label for files.',
                    default='new_species')

args = parser.parse_args()



def initial_check():
    """
    Summarizes the inputs to the script in addition to the choice of model features & hyperparameters to fit.
    """
    
    #reports species name
    print('Species name: {}.'.format(args.species_name))

    #reports test expression data being used
    print('Test expression matrix selected: mapping orthologs for {}.'.format(args.x_test))

    #reports orthologs gene will map to.
    print('Ortholog list: genes will be mapped to orthologs in {}.'.format(args.ortholog_list))

    #check if sampling times are included for test data, if not will return just use original labels in exp matrix
    if args.target_test is None:
         print('Test sampling times: No test sampling times provided. Will keep origianl labels in expression matrix.')
    else:
        print('Test sampling times: Sampling times provided from {}.'.format(args.target_test))


def average_duplicate_orthologs(expression_matrix):
    """
    Identifies duplicated ortholog genes in the expression matrix and averages their expression to
    ensure gene features in the training data correspond with gene features in the test data.
    Parameters
    ----------
    expression_data : pd.DataFrame
        The expression matrix of the test species after replacing genes with orthologs of the training species.
    Returns
    ----------
    average_expression : pd.DataFrame
        The expression matrix of the test species after averaging the expression values of duplicated ortholog genes.
    """
    gene_name = []
    av_exp = []

    for i in expression_matrix.index:
        i_exp = expression_matrix.loc[i]
        if len(i_exp.shape) > 1:
            av_exp.append(np.mean(i_exp, axis=0))

        else:
            av_exp.append(i_exp)
        gene_name.append(i)

    av_exp = pd.concat(av_exp,axis=1).T

    av_exp.index = gene_name

    return av_exp

def load_data(expression_data, ortholog_list):
    """
    Loads test species expression data and ortholog lists. The gene index of the test species is replaced
    with orthologous genes of the training data.

    Parameters
    ----------
    expression_data : str
        The file path for the CSV file containing the gene expression matrix of the test species
    ortholog_list : str
        The file path for the CSV file containing the ortholog gene mappings in the test species and the training species 
        Requires: 
            column 0 : genes of the test species
            column 1 : genes of the training species
        
    Returns
    ----------
    ortholog_expression : pd.DataFrame
        The expression matrix of the test species, with index including orthologous genes of the training species.
    """
    #load test species expression matrix
    x_data = pd.read_csv(expression_data, index_col=0)

    #load list of ortholog gene mappings between test species and the species used in training
    x_orthologs = pd.read_csv(ortholog_list)

    #set test species genes to index of ortholog list
    x_orthologs.index = x_orthologs.iloc[:,0]

    #drop any genes with no mappings
    x_orthologs = x_orthologs.dropna()

    #ensure test species genes are cosistent between expression matrix and ortholog list
    features = np.intersect1d(x_data.index, x_orthologs.index)

    #script will terminate if no genes correspond between the expression matrix and the ortholog list
    if len(features) == 0:
        print('ERROR: zero genes intersect between test species expression matrix and ortholog list. Script terminated.')
        sys.exit()

    x_orthologs = x_orthologs.loc[features]
    x_data = x_data.loc[x_orthologs.index]

    #replace genes of the test species with orthologous genes belonging to the training species
    x_data.index = x_orthologs.iloc[:,1]

    #since genes tend to map to multiple possible orthologs, run function to average duplicated training species genes
    ortholog_expression = average_duplicate_orthologs(x_data)
    ortholog_expression = ortholog_expression.sort_index()

    return ortholog_expression


def label_samples(expression_data, time_labels):
    """
    Labels the target data samples/columns with sampling times.
    Parameters
    ----------
    expression_data : pd.DataFrame
        The file path for the CSV file containing the gene expression matrix of the test species
    time_labels : str
        The file path for the CSV file containing the ortholog gene mappings in the test species and the training species
        Requires:
            column 0 : column number of each sample
            column 1 : sampling times

    Returns
    ----------
    labelled_expression : pd.DataFrame
        The expression matrix of the test species, with column names being replaced with sampling times.
    """

    time_labels = pd.read_csv(time_labels, index_col=0)

    labelled_expression = expression_data.copy()
    labelled_expression.columns = time_labels.iloc[:,0]

    return labelled_expression

def main():
    #summarize the inputs
    initial_check()

    #load test expression data and map orthologs from test species to training species
    x_test = load_data(args.x_test, args.ortholog_list)

    #if time labels available, replace expression matrix column names with them
    if args.target_test is not None:
        x_test = label_samples(x_test, args.target_test)

    x_test.to_csv(args.out_results+'/'+args.species_name+'_orthologs.csv')


    
if __name__ == "__main__":
    main()

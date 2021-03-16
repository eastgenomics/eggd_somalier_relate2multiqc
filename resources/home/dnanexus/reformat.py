import pandas as pd
import argparse


def parse_args():
    """Parse through arguements


    Returns:
        args: Variable that you can extract relevant
        arguements inputs needed
    """
    # Read in arguments
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '-i', '--input_data',
        help='default cutoff is >= 45',
        required=False
        )

    parser.add_argument(
        '-F', '--Female_cutoff',
        help='default cutoff is >= 45',
        required=False
        )

    parser.add_argument(
        '-M', '--Male_cutoff',
        help='default cutoff is <= 1',
        required=False
        )

    args = parser.parse_args()

    return args


def Rename_dataframe(data):
    """REmoves hashtag from familyID and makes sampleID 1st column

    Args:
        data: unformatted somalier dataframe

    Returns:
        dataframe: reordered dataframe with no hashtag for familyID
    """
    data.columns = [
        'family_id', 'sample_id', 'paternal_id',
        'maternal_id', 'sex', 'phenotype', 'original_pedigree_sex',
        'gt_depth_mean', 'gt_depth_sd', 'depth_mean', 'depth_sd',
        'ab_mean', 'ab_std', 'n_hom_ref', 'n_het', ' n_hom_alt',
        'n_unknown', 'p_middling_ab', 'X_depth_mean', 'X_n',
        'X_hom_ref', 'X_het', 'X_hom_alt', 'Y_depth_mean', 'Y_n'
        ]

    data = data[[
        'sample_id', 'paternal_id', 'maternal_id', 'family_id',
        'sex', 'phenotype', 'original_pedigree_sex', 'gt_depth_mean',
        'gt_depth_sd', 'depth_mean', 'depth_sd', 'ab_mean', 'ab_std',
        'n_hom_ref', 'n_het', ' n_hom_alt', 'n_unknown',
        'p_middling_ab', 'X_depth_mean', 'X_n', 'X_hom_ref',
        'X_het', 'X_hom_alt', 'Y_depth_mean', 'Y_n']]

    samples = data.sample_id

    # Check that there are no sample name duplicates
    if len(samples) == len(set(samples)):
        # TRUE len samples equal to uniques len samples
        print("Unique sampleIDs")
    else:
        print('len(samples) =', len(samples))
        print('len(set(samples)) =', len(set(samples)))
        print("Duplicates sampleIDs")

    return data


def get_cutoffs(args):
    """Pulls out thresholds from arguments

    Args:
        args (variable): Contains all input arguments

    Returns:
        f_cuttoff (int): female het calls threshold
        m_cuttoff (int): male het calls threshold
    """
    # If cutoffs are provided use those else
    # use default cutoffs F = 45 and M = 1

    if args.Female_cutoff is None:
        print("Default female cutoff at >= 45 is used")
        f_cutoff = 45
    else:
        print("Female cutoff is " + args.Female_cutoff)
        f_cutoff = args.Female_cutoff

    if args.Male_cutoff is None:
        print("Default Male cutoff at <= 1 is used")
        m_cutoff = 1
    else:
        print("Male cutoff is " + args.Male_cutoff)
        m_cutoff = args.Male_cutoff

    # Need to convert to int as its str so far
    f_cutoff = int(f_cutoff)
    m_cutoff = int(m_cutoff)

    return f_cutoff, m_cutoff


def Predict_Sex(data, f_cutoff, m_cutoff):
    """Predicts sex on data provided based on given / default thresholds

    Args:
        data (panda data frame): output from {sample}.somalier.samples.tsv
        f_cutoff (int): from -F input provided as arg
        m_cutoff (int): from -M input provided as arg

    Returns:
        data (pandas data frame): Updates dataframe
        including predicted sex column
    """
    PredictedSex = []
    x_het = list(data.X_het)

    for x in x_het:
        if x >= f_cutoff:
            PredictedSex.append("female")
        elif x <= m_cutoff:
            PredictedSex.append("male")
        else:
            PredictedSex.append("unknown")

    Predicted_Sex = pd.DataFrame({'Predicted_Sex': PredictedSex})

    data = pd.concat([data, Predicted_Sex], axis=1)

    return data

def Matching_Sexes(data):
    """Gives true or false whether reported or predicted sex match

    Args:
        data (panda data frame): output from {sample}.somalier.samples.tsv

    Returns:
        data (pandas data frame): Updates dataframe
        including predicted sex column
    """
    Reported_Sex = list(data.original_pedigree_sex)
    Predicted_Sex = list(data.Predicted_Sex)
    Match = []

    for sample in range(0,len(Reported_Sex)):
        reported_sex_sample = Reported_Sex[sample]
        predicted_sex_sample = Predicted_Sex[sample]
        sex_match = reported_sex_sample == predicted_sex_sample
        Match.append(sex_match)
    
    # Match list is a booleans and not strings so we hard to apply 
    # string functions. Convert each boolean to string
    # 

    Match_lowercase = []

    for boolean in Match:
        boolean_string = str(boolean)
        boolean_string_lowercase = boolean_string.lower()
        Match_lowercase.append(boolean_string_lowercase)

    print(Match_lowercase)

    Match_Sexes = pd.DataFrame({'Match_Sexes': Match_lowercase})

    data = pd.concat([data, Match_Sexes], axis=1)

    return data

def main():

    args = parse_args()

    data = pd.read_csv(args.input_data, sep='\t')

    data = Rename_dataframe(data)

    f_cutoff, m_cutoff = get_cutoffs(args)

    data = Predict_Sex(data, f_cutoff, m_cutoff)

    data = Matching_Sexes(data)

    # replace over existing file
    data.to_csv(
        'Multiqc_' + args.input_data,
        sep="\t", index=False, header=True
        )


if __name__ == "__main__":

    main()

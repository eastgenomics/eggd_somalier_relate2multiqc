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
        '-i', '--input_somalier',
        help='Somalier samples tsv file',
        required=True
        )

    parser.add_argument(
        '-F', '--Female_cutoff',
        help='An integer value for het calls threshold for females, assigns as female for equal & above threshold',
        required=False,
        nargs='?',
        const=45,
        default=45,
        type=int
        )

    parser.add_argument(
        '-M', '--Male_cutoff',
        help='An integer value for het calls threshold for males, assigns as female for equal & below threshold',
        required=False,
        nargs='?',
        const=1,
        default=1,
        type=int
        )

    args = parser.parse_args()

    return args


def rename_dataframe(data):
    """Removes hashtag from familyID and makes sampleID 1st column

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
        print('Number of samples =', len(samples))
        print('Unique samples =', len(set(samples)))
        print("Duplicates sampleIDs")
        raise Exception('Duplicates sampleIDs')

    return data


def get_cutoffs(args):
    """Pulls out thresholds from arguments

    Args:
        args (variable): Contains all input arguments

    Returns:
        f_cuttoff (int): female het calls threshold
        m_cuttoff (int): male het calls threshold
    """
    f_cutoff = args.Female_cutoff
    m_cutoff = args.Male_cutoff

    return f_cutoff, m_cutoff


def predict_sex(data, f_cutoff, m_cutoff):
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


def matching_sexes(data):
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

    for sample in range(0, len(Reported_Sex)):
        reported_sex_sample = Reported_Sex[sample]
        predicted_sex_sample = Predicted_Sex[sample]
        sex_match = reported_sex_sample == predicted_sex_sample
        Match.append(sex_match)

    # Match list is a booleans and not strings so we hard to apply
    # string functions. Convert each boolean to string

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

    data = pd.read_csv(args.input_somalier, sep='\t')

    data = rename_dataframe(data)

    f_cutoff, m_cutoff = get_cutoffs(args)

    data = predict_sex(data, f_cutoff, m_cutoff)

    data = matching_sexes(data)

    # replace over existing file
    data.to_csv(
        'Multiqc_' + args.input_somalier,
        sep="\t", index=False, header=True
        )


if __name__ == "__main__":

    main()

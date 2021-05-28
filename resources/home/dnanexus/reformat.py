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


def update_sex_pedigree(data):
    """Updates original_pedigree_sex to differentiate 0 and 3.

    New function to update original_pedigree_sex so 0 = unknown and 
    3 = none. This enables later stage in multiqc to show the two
    states (0 and 3) different.

    Args:
        data (panda data frame): output from {sample}.somalier.samples.tsv
    
    Returns:
        data (pandas data frame): Updated original_pedigree_sex column
    """
    original_sex_column = list(data.sex)
    new_pedigree_sex_column = []
    
    # loop through each sex, assign as follows to new list:
    # 0 = unknown, 1 = male, 2 = female, 3 = none
    for sex in original_sex_column:
        if sex == 0:
            new_pedigree_sex_column.append("unknown")
        elif sex == 1:
            new_pedigree_sex_column.append("male")
        elif sex == 2:
            new_pedigree_sex_column.append("female")
        elif sex == 3:
            new_pedigree_sex_column.append("none")
        elif sex >= 4:
            raise Exception("Sex in original_pedigree_sex_column column"
                    "is not categorised as 0,1,2,3."
                    "Check eggs_somalier_relate applet")

    print(original_sex_column)
    print(new_pedigree_sex_column)
    # replace the original_pedigree_sex column with the sex as female,
    # male, uknown and none 
    data["original_pedigree_sex"] = new_pedigree_sex_column

    return data


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

    # For every row, state whether they match between reported and
    # predicted sex. If reported is unknown, then match is NA
    for sample in range(0, len(Reported_Sex)):
        reported_sex_sample = Reported_Sex[sample]
        predicted_sex_sample = Predicted_Sex[sample]
        if reported_sex_sample == "unknown":
            Match.append("NA")
        elif reported_sex_sample == "none":
            Match.append("NA")
        else:
            sex_match = reported_sex_sample == predicted_sex_sample
            Match.append(sex_match)

    # Match list is a booleans and not strings so we hard to apply
    # string functions. Convert each boolean to string

    Match_lowercase = []

    for boolean in Match:
        boolean_string = str(boolean)
        boolean_string_lowercase = boolean_string.lower()
        Match_lowercase.append(boolean_string_lowercase)

    # Return the na to NA
    Match_lowercase = [word.replace('na', 'NA') for word in Match_lowercase]

    print(Match_lowercase)

    Match_Sexes = pd.DataFrame({'Match_Sexes': Match_lowercase})

    data = pd.concat([data, Match_Sexes], axis=1)

    return data


def main():

    args = parse_args()

    data = pd.read_csv(args.input_somalier, sep='\t')

    # update the sex pedigree to correctly match the sex integers
    data = update_sex_pedigree(data)

    # rename dataframe to be compatible in multiqc report
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

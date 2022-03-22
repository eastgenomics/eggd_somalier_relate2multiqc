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
        '-F', '--female_cutoff',
        help='An integer value for het calls threshold for females, assigns as female for equal & above threshold',
        required=False,
        nargs='?',
        const=45,
        default=45,
        type=int
        )

    parser.add_argument(
        '-M', '--male_cutoff',
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
    f_cutoff = args.female_cutoff
    m_cutoff = args.male_cutoff

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
    # male, unknown and none
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
    predictedsex = []
    x_het = list(data.X_het)

    for x in x_het:
        if x >= f_cutoff:
            predictedsex.append("female")
        elif x <= m_cutoff:
            predictedsex.append("male")
        else:
            predictedsex.append("unknown")

    predicted_sex = pd.DataFrame({'Predicted_Sex': predictedsex})

    data = pd.concat([data, predicted_sex], axis=1)

    return data


def matching_sexes(data):
    """Gives true or false whether reported or predicted sex match

    Args:
        data (panda data frame): output from {sample}.somalier.samples.tsv

    Returns:
        data (pandas data frame): Updates dataframe
        including predicted sex column
    """

    # somalier relate states that anything that is not 1 or 2 is
    # unknown. But we need to classify 3's as None as they are not provided

    mappings={'0': 'unknown', '1': 'male', '2':'female', '3': 'none'}

    # map the intergers in data['sex'] column to the strings in mapping
    # dictionary. Then appply the output directory to the data frame column

    data['original_pedigree_sex'] = data['sex'].apply(
                                    lambda x: mappings.get(str(x))
                                    )

    # Need to create a column called match that has true/false boolean 
    # for every row, stating whether they match between reported and
    # predicted sex. If reported is unknown/none, then match is NA

    data["Match_Sexes"] = "NA"

    # If reported sex is not unknown or none, then see if reported and 
    # predicted sex is a match (false/true boolean)
    for idx, row in data.iterrows():
        if not (row['original_pedigree_sex'] == "unknown" or row['original_pedigree_sex'] == "none" or row['Predicted_Sex'] == "unknown"):
            data.at[idx, 'Match_Sexes'] = row['original_pedigree_sex'] == row['Predicted_Sex']
        else:
            if (row['original_pedigree_sex'] == "unknown" or row['Predicted_Sex'] == "unknown" or row['original_pedigree_sex'] == "none"):
                data.at[idx, 'Match_Sexes'] = "NA"
            # need to make the false/true boolean to string to make it 
            # lower case for multiqc
            data.at[idx, 'Match_Sexes'] = str(data.at[idx, 'Match_Sexes']).lower()

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

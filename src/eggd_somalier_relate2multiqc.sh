#!/bin/bash

# stop running is error appears and print code & messages
set -exo pipefail


main() {

    echo "Value of somalier_file: '$input_file'"

    echo "Value of female: '${f}'"

    echo "Value of male: '${m}'"

    # Install packages
    pip install packages/pandas-0.24.2-cp35-cp35m-manylinux1_x86_64.whl

    # Load data
    dx-download-all-inputs
    find ~/in -type f -name "*" -print0 | xargs -0 -I {} mv {} ./

    # Add predicted sex to file based on x_het
    echo "-------------- Predicting sex based on threshold -----------------"
    chmod 777 *
    # Add threshold to file
    # if statement -z assumes the parameter is null
    if [[ ! -z ${f} ]] && [[ ! -z ${m} ]]; then
        echo "Inputted thresholds will be used: Female =<" "${f} and" "male =>" "${m}"
        python3 reformat.py -F ${f} -M ${m} -i *somalier.samples.tsv
    elif [[ ! -z ${f} ]] && [[ -z ${m} ]]; then
        echo "Female threshold set to" "${f}." "Default threshold for male =< 1 het calls will be used."
        python3 reformat.py -F ${f} -M 1 -i *somalier.samples.tsv
    elif [[  -z ${f} ]] && [[ ! -z ${m} ]]; then
        echo "Male threshold set to" "${m}." "Default threshold for female => 45 het calls will be used."
        python3 reformat.py -F 45 -M ${m} -i *somalier.samples.tsv
    else
        echo "No inputs provided. Default het call thresholds of female => 45 and male =< 1 are used."
        python3 reformat.py -F 45 -M 1 -i *somalier.samples.tsv
    fi

    echo "--------------Outputting files -----------------"
    mkdir -p /home/dnanexus/out/somalier_output/

    mv Multiqc_* /home/dnanexus/out/somalier_output/

    dx-upload-all-outputs
}

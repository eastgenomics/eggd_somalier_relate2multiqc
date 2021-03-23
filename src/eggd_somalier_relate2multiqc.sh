#!/bin/bash

# stop running is error appears and print code & messages
set -exo pipefail


main() {

    echo "File input for somalier_file: '$somalier_input'"

    echo "Value of female threshold: '${female_threshold}'"

    echo "Value of male threshold: '${male_threshold}'"

    # Install packages
    pip install packages/pandas-0.24.2-cp35-cp35m-manylinux1_x86_64.whl

    # Load data
    dx-download-all-inputs

    # Since we using the input later as the output's filename, its 
    # easier to move the file to where the script it
    mv in/somalier_input/*somalier.samples.tsv .

    # Add predicted sex to file based on x_het
    echo "-------------- Predicting sex based on threshold -----------------"
    chmod 777 *

    # if no inputs provided, it uses defaults in reformat.py 
    python3 reformat.py -F ${female_threshold} -M ${male_threshold} -i *somalier.samples.tsv

    echo "--------------Outputting files -----------------"
    mkdir -p /home/dnanexus/out/modified_somalier_output/

    mv Multiqc_* /home/dnanexus/out/modified_somalier_output/

    dx-upload-all-outputs
}

#!/bin/bash

# stop running is error appears and print code & messages
set -exo pipefail


main() {

    echo "Value of somalier_file: '$somalier_input'"

    echo "Value of female: '${female_threshold}'"

    echo "Value of male: '${male_threshold}'"

    # Install packages
    pip install packages/pandas-0.24.2-cp35-cp35m-manylinux1_x86_64.whl

    # Load data
    dx-download-all-inputs
    find ~/in -type f -name "*" -print0 | xargs -0 -I {} mv {} ./

    # Add predicted sex to file based on x_het
    echo "-------------- Predicting sex based on threshold -----------------"
    chmod 777 *

    python3 reformat.py -F ${female_threshold} -M ${male_threshold} -i *somalier.samples.tsv

    echo "--------------Outputting files -----------------"
    mkdir -p /home/dnanexus/out/modified_somalier_output/

    mv Multiqc_* /home/dnanexus/out/modified_somalier_output/

    dx-upload-all-outputs
}

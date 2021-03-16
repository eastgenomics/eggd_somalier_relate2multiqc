# eggd_somalier_relate2multiqc

## What does this app do?
Reformats the output of somalier relate to append predicted sex, add a matching column to state whether sample's predicted sex is a true or false match to reported sex. The app also reorders columns to present data clearly in MultiQC report.

![Image of workflow](https://github.com/eastgenomics/eggd_somalier_relate2multiqc/blob/dev/Somalier_relate2multiqc_workflow.jpg)

## What are the inputs?
* somalier.samples.tsv
* Thresholds to predict sex from x_het
    * female = 45, male = 1 for geminini(dias) samples


## What are the outputs?

* Multiqc_somalier.samples.tsv


## Where is this app applicable?
If you want to add predicted sex column and present data in MultiQC report.


### This app was made by EMEE GLH

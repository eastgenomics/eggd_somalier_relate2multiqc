# eggd_somalier_relate2multiqc

## What does this app do?
Reformats the output of somalier relate to append predicted sex, add a matching column to state whether sample's predicted sex is a true or false match to reported sex. The app also reorders columns to present data clearly in MultiQC report.

![Image of workflow](Somalier_relate2multiqc_workflow.jpg)

## What are the inputs?
* somalier.samples.tsv
* Female and male thresholds to predict sex from x_het variant calls
    * female = 45, male = 1 are used for default
    * Anything between the female and male threshold is classified as unknown sex


## What are the outputs?

* Multiqc_somalier.samples.tsv


## Where is this app applicable?
If you want to add predicted sex column and present data in MultiQC report.


### This app was made by EMEE GLH

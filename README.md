odl_user_171120@udacitylabs.onmicrosoft.com
rnmm66MCG*Hg
# Ofurufu
`Ofurufu` means sky/aerospace in Yoruba, as in `oko ofurufu` which means aeroplane.

Ofurufu, as a project, builds an automated passenger boarding system which comprises
* Passenger verification (Name & identity)
* Luggage validation: Flagging luggages with banned items (lighters, currently)
* Flight information verification/cross-referencing

Passengers are co-ordinated according to the verification results of this system. Additionally, the experience of the travelers are monitored using sentiment and emotion analysis.

All these are done with the aim of speeding up the passenger boarding time and improving experience for them.

## Services 
This project relies on a number of Azure services and their SDKs
- Storage Account
- Face Cognitive Service
- Form Recognizer Cognitive Service
- Computer Vision Cognitive Service
- Azure Video Analyzer/Indexer

An azure subscription is thus necessary to setup and run this project. 

## Setup and Installation
* Clone this repository
```
git clone https://github.com/theyorubayesian/ofurufu.git
```
* Create a conda environment using the `environment.yml` file and activate it
```
conda env create -f environment.yml
conda activate ofurufu
```
* Create the above listed Azure services. Detailed instructions can be found [here](https://docs.microsoft.com/en-us/azure/cognitive-services/cognitive-services-apis-create-account?tabs=multiservice%2Cwindows)

## Project Instructions
* Upload the files in the `material_preparation_step` folder to Azure blob storage.
This section should contain all the student deliverables for this project.
* Train a custom Form Recognizer model for boarding passes using this [Azure website](https://fott.azurewebsites.net/). Use the boarding passes in the `material_preparation_step/boarding_pass/training_data` folder as training data.
* Train a custom lighter detection model using the data in `starter/lighter_images` and [Azure Custom Vision](https://azure.microsoft.com/en-us/services/cognitive-services/custom-vision-service/)

## Submission Info
All scripts are contained in the [ofurufu](ofurufu/)

* [Item1](www.item1.com) - Description of item
* [Item2](www.item2.com) - Description of item
* [Item3](www.item3.com) - Description of item

Include all items used to build project.

## License

[License](LICENSE.txt)

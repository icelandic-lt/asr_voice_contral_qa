# Voice control and Question answering models

The goal of this work package was to develop Kaldi recipes for voice control and question answering systems for Icelandic. Voice control refers to one-way communication between humans and systems to solicit an action. We defined six tasks and either generated or gathered data for each, normalized the data and trained Kaldi language models.

# Directory
As this project involved creating models for possible use cases where the end user is unknown or the developer for that fact, we focused on generating and cleaning the data. The data generated is a file called `train`, one for each task. The scripts used to generate or gather the data are listed in a later chapter. 


The models are accompanied by the file `main.conf` that can be used to set up an ASR server using [Tiro Speech Core (TSC)](https://github.com/icelandic-lt/tiro-speech-core). The code used to generate/gather and clean the data, and create the models is in the folder `code` but we recommend going to the GitHub repositories as it might have been updated. The repositories are linked in the following chapters. 

```
├── README.md
├── models
|   ├── addresses
│       ├── conf                        Decoding configurations.
│       ├── final.mdl                   The acoustic model.
│       ├── frame_subsampling_factor    Acoustic model configurations.
│       ├── G.fst                       Grammer FST used when decoding with Kaldi.
│       ├── graph                       The decoding graph.
│       ├── ivector_extractor           Ivector extractor and configurations.
│       ├── main.conf                   File used by TSC to configure the decoding.
│       ├── phones.txt                  Phoneme set used while training the model.
│       ├── results                     Results from the decoding the test set.
│       ├── test                        Format<id-sentence>. The id format is: <index_TTS voice id> .
│       ├── train                       Language model training text.
│       └── tree                        Acoustic model configurations.
│   ├── kennitolur
│   ├── names
│   ├── phone_numbers
│   ├── trivia
│   └── unit-conversion
├── code                                Archives/submodules of all the code repositories. 
│   ├── create_models-M9
│   ├── fstring2fst-M9
│   ├── is-trivia-questions-M9
│   ├── lm-is-forms-M9
│   ├── numi-M9
│   └── unit-conversion-M9
├── data
│   ├── addresses
|       ├── lexicon                     The vocabulary along with the phoneme transcription of each word. 		
|       ├── test                        Format<id-sentence>. The id format is: <index_TTS voice id>.
│       └── train                       Language model training text.
│   ├── kennitolur
│   ├── names
│   ├── phone_numbers
│   ├── trivia
│   └── unit-conversion
```


# The models
We trained a 4-gram language model for each task using tools in [Kaldi](https://github.com/kaldi-asr/kaldi) and [KenLM](https://kheafield.com/code/kenlm/) and compiled a decoding graph. The accompanying acoustic model is a 
TDNN model that was trained using the [Alþingi corpus](https://repository.clarin.is/repository/xmlui/handle/20.500.12537/277)/). The recipe for the language model is on [Github](https://github.com/icelandic-lt/asr_create_models) along with the evaluation scripts.

## Evaluation
As these are task-specific models and should just cover a limited amount of vocabulary the test set was created by taking random sentences from the training data. We generated examples using the TTS voices on tts.tiro.is. TTS-generated data can have its artefacts which can affect the ASR model so we compare the results to a general large vocabulary model.  


The WER is as follows: 
| Model                   | %WER task-specific model | %WER general |
| ----------------------- | ------------------------ | ------------ |
| Addresses               | 37.38                    | 80.75        |
| Social security numbers | 15.81                    | 44.89        |
| Names                   | 22.46                    | 104.17       |
| Trivia                  | 19.60                    | 48.15        |
| Phone numbers           | 16.66                    | 40.01        |
| Unit Conversion         | 5.37                     | 27.48        |

As expected the task-specific models perform a lot better than the general model. The names are especially difficult for the general model which are present in the Addresses and the Names tasks. There are most likely some OOV words in the general model.  


## Unit conversion
The thought here was to create a model for common queries with multiple unit conversion tasks. We generated training data based on template sentences where the unit (distance, currency, volume, etc.) and a number was added in the right inflection. Some examples are:
```
Isl: Hversu margar íslenskar krónur fæ ég fyrir einn dollara?
Eng: How many Icelandic kronur do I get for one dollar?
    
Isl: Hvað er einn desilítri margir lítrar?
Eng: What is one deciliter many liters? 

Isl: Breyttu fimm mílum í kílómetra
    Eng: Convert five miles into kilometers
```
The sentence generation script is on [Github](https://github.com/icelandic-lt/unit-conversion). For this script we needed a list of numbers in the expend form along with the inflection. Because of the high number of inflections for each number this is a non trivial task, for that reason we wrote a tool called Númi which writes the numbers out given an integer and inflection e.g.

```
Input: 92, "ft_hk_ef"
Output: níutíu og tveggja

Input: 121, "ft_kk_þgf",
Output: "eitt hundrað tuttugu og einum", "hundrað tuttugu og einum"
```
The code for this tool is on [Github](https://github.com/icelandic-lt/numi) and is available as a pip package `pip install numi`.

## Trivia questions
We gathered data from three sources; from question authors on a local game show Gettu betur, from an open source collection of [Trivia-question](https://github.com/sveinn-steinarsson/is-trivia-questions) and from a question answering crowdsourcing platform called [Spurningar.is](https://spurningar.is). We were not able to get permission to make the questions from the Gettu betur authors publicly available so they were solely used for the model training.

The data is as follows. 

| Source              | Number of sentences |
| ------------------- | ------------------- |
| is-trivia-questions | 11309               |
| Gettu Betur         | 4184                |
| Spurning.is         | 18304               |

 
The data was normalized with regards to numbers and abbreviations using [Regina](https://github.com/icelandic-lt/regina_normalizer) along with some manual parsing. The scripts and data for the open source part is available on [Github](https://github.com/icelandic-lt/is-trivia-questions).

## Form fields
The next four tasks focus on common attributes needed for various purposes that need special attention regarding vocabulary and language model structure. We chose attributes that are common to many tasks keeping in mind to get a wide range of attribute types. This way it is possible to reconfigure or adapt the models to a variety of new tasks. The four attributes chosen are home addresses, full names, personal id numbers (kennitala) and phone numbers.  The code for these task is available on [Github](https://github.com/icelandic-lt/lm-is-forms).

### Home addresses
The national registry has a list of all (legal) home addresses in Iceland. This data is available on their website, [skra.is](https://skra.is/). The addresses were normalized with handwritten rules for each special address type. 

### Names
To generate names we used the BIN database to collect first names, middle names and surnames (both patronymic and matronymic). No normalization step was needed for this attribute. 

### Personal identification numbers (kennitala)
Every Icelandic person and company has a personal identification number used for identification in various tasks. The number follows a specific verifiable pattern and can be read out in various different ways. For example the personal identification number “241270 2329” can be read like any of the following representations:

```
tveir fjórir einn tveir sjö núll tveir þrír tveir níu
tuttugu og fjórir tólf sjötíu tuttugu og þrír tuttugu og níu
tuttugu og fjórir tólf sjötíu tuttugu og þrír tveir níu
tuttugu og fjórir tólf sjötíu tveir þrír tuttugu og níu
tuttugu og fjórir tólf sjötíu tveir þrír tveir níu
tuttugu og fjórir tólf sjö núll tveir þrír tveir níu
tuttugu og fjórir tólf sjö núll tveir þrír tuttugu og níu
tuttugu og fjórir tólf sjö núll tuttugu og þrír tveir níu
tuttugu og fjórir tólf sjö núll tuttugu og þrír tuttugu og níu
tveir fjórir tólf sjö núll tuttugu og þrír tuttugu og níu
tuttugu og fjórir einn tveir sjötíu tuttugu og þrír tuttugu og níu
```

We generated a long list of possible identification numbers and normalized each one in up to eleven different forms to allow for different readings of each number.

### Phone numbers
The phone numbers were generated and normalized in a similar way to the personal identification numbers. We generated a list of possible phone numbers and spelled each one out in nine different ways to allow for different readings of the numbers.


# LICENCE
http://creativecommons.org/licenses/by/4.0/

# Acknowledgements
This project was funded by the Language Technology Programme for Icelandic 2019-2023. The programme, which is managed and coordinated by Almannarómur, is funded by the Icelandic Ministry of Education, Science and Culture.

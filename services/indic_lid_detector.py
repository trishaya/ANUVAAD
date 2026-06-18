# import packages

import os
import re
import pandas as pd

import fasttext

import torch
from torch.utils.data import Dataset
from transformers import AutoTokenizer


class IndicBERT_Data(Dataset):

    def __init__(self, indices, X):

        self.size = len(X)
        self.x = X
        self.i = indices

    def __len__(self):
        return self.size

    def __getitem__(self, idx):

        text = self.x[idx]
        index = self.i[idx]

        return tuple([index, text])


class IndicLID():

    def __init__(self, input_threshold=0.5, roman_lid_threshold=0.6):

        self.device = torch.device(
            'cuda:0' if torch.cuda.is_available() else 'cpu'
        )

        # ================= BASE DIR =================

        BASE_DIR = os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))
        )

        # ================= MODEL PATHS =================

        self.IndicLID_FTN_path = os.path.join(
            BASE_DIR,
            'models',
            'indiclid-ftn',
            'model_baseline_roman.bin'
        )

        self.IndicLID_FTR_path = os.path.join(
            BASE_DIR,
            'models',
            'indiclid-ftr',
            'model_baseline_roman.bin'
        )

        self.IndicLID_BERT_path = os.path.join(
            BASE_DIR,
            'models',
            'indiclid-bert',
            'basline_nn_simple.pt'
        )

        # ================= LOAD MODELS =================

        self.IndicLID_FTN = fasttext.load_model(
            self.IndicLID_FTN_path
        )

        self.IndicLID_FTR = fasttext.load_model(
            self.IndicLID_FTR_path
        )

        self.IndicLID_BERT = torch.load(
            self.IndicLID_BERT_path,
            map_location=self.device,
            weights_only=False
        )

        self.IndicLID_BERT.eval()

        self.IndicLID_BERT_tokenizer = AutoTokenizer.from_pretrained(
            "ai4bharat/IndicBERTv2-MLM-only"
        )

        self.input_threshold = input_threshold
        self.model_threshold = roman_lid_threshold

        # ================= LABEL MAP =================

        self.IndicLID_lang_code_dict_reverse = {

            0: 'asm_Latn',
            1: 'ben_Latn',
            2: 'brx_Latn',
            3: 'guj_Latn',
            4: 'hin_Latn',
            5: 'kan_Latn',
            6: 'kas_Latn',
            7: 'kok_Latn',
            8: 'mai_Latn',
            9: 'mal_Latn',
            10: 'mni_Latn',
            11: 'mar_Latn',
            12: 'nep_Latn',
            13: 'ori_Latn',
            14: 'pan_Latn',
            15: 'san_Latn',
            16: 'snd_Latn',
            17: 'tam_Latn',
            18: 'tel_Latn',
            19: 'urd_Latn',
            20: 'eng_Latn',
            21: 'other',

            22: 'asm_Beng',
            23: 'ben_Beng',
            24: 'brx_Deva',
            25: 'doi_Deva',
            26: 'guj_Gujr',
            27: 'hin_Deva',
            28: 'kan_Knda',
            29: 'kas_Arab',
            30: 'kas_Deva',
            31: 'kok_Deva',
            32: 'mai_Deva',
            33: 'mal_Mlym',
            34: 'mni_Beng',
            35: 'mni_Meti',
            36: 'mar_Deva',
            37: 'nep_Deva',
            38: 'ori_Orya',
            39: 'pan_Guru',
            40: 'san_Deva',
            41: 'sat_Olch',
            42: 'snd_Arab',
            43: 'tam_Tamil',
            44: 'tel_Telu',
            45: 'urd_Arab'
        }

    # ================= PREPROCESS =================

    def pre_process(self, input):
        return input

    # ================= CHARACTER CHECK =================

    def char_percent_check(self, input):

        input_len = len(list(input))

        special_char_pattern = re.compile(
            '[@_!#$%^&*()<>?/\|}{~:]'
        )

        special_char_matches = special_char_pattern.findall(input)

        special_chars = len(special_char_matches)

        spaces = len(re.findall('\s', input))
        newlines = len(re.findall('\n', input))

        total_chars = input_len - (
            special_chars + spaces + newlines
        )

        en_pattern = re.compile('[a-zA-Z0-9]')

        en_matches = en_pattern.findall(input)

        en_chars = len(en_matches)

        if total_chars == 0:
            return 0

        return (en_chars / total_chars)

    # ================= FTN =================

    def native_inference(self, input_list, output_dict):

        if not input_list:
            return output_dict

        input_texts = [line[1] for line in input_list]

        predictions = self.IndicLID_FTN.predict(input_texts)

        for input, pred_label, pred_score in zip(
            input_list,
            predictions[0],
            predictions[1]
        ):

            output_dict[input[0]] = (
                input[1],
                pred_label[0][9:],
                pred_score[0],
                'IndicLID-FTN'
            )

        return output_dict

    # ================= FTR =================

    def roman_inference(self, input_list, output_dict, batch_size):

        if not input_list:
            return output_dict

        input_texts = [line[1] for line in input_list]

        predictions = self.IndicLID_FTR.predict(input_texts)

        bert_inputs = []

        for input, pred_label, pred_score in zip(
            input_list,
            predictions[0],
            predictions[1]
        ):

            if pred_score[0] > self.model_threshold:

                output_dict[input[0]] = (
                    input[1],
                    pred_label[0][9:],
                    pred_score[0],
                    'IndicLID-FTR'
                )

            else:
                bert_inputs.append(input)

        output_dict = self.IndicBERT_roman_inference(
            bert_inputs,
            output_dict,
            batch_size
        )

        return output_dict

    # ================= BERT =================

    def IndicBERT_roman_inference(
        self,
        bert_inputs,
        output_dict,
        batch_size
    ):

        if not bert_inputs:
            return output_dict

        df = pd.DataFrame(bert_inputs)

        dataloader = self.get_dataloaders(
            df.iloc[:, 0],
            df.iloc[:, 1],
            batch_size
        )

        with torch.no_grad():

            for data in dataloader:

                batch_indices = data[0]
                batch_inputs = data[1]

                embeddings = self.IndicLID_BERT_tokenizer(
                    batch_inputs,
                    return_tensors="pt",
                    padding=True,
                    truncation=True,
                    max_length=512
                )

                embeddings = embeddings.to(self.device)

                outputs = self.IndicLID_BERT(
                    embeddings['input_ids'],
                    token_type_ids=embeddings['token_type_ids'],
                    attention_mask=embeddings['attention_mask']
                )

                _, predicted = torch.max(outputs.logits, 1)

                for index, input, pred_label, logit in zip(
                    batch_indices,
                    batch_inputs,
                    predicted,
                    outputs.logits
                ):

                    output_dict[index] = (
                        input,
                        self.IndicLID_lang_code_dict_reverse[
                            pred_label.item()
                        ],
                        logit[pred_label.item()].item(),
                        'IndicLID-BERT'
                    )

        return output_dict

    # ================= POST PROCESS =================

    def post_process(self, output_dict):

        results = []

        keys = list(output_dict.keys())

        keys.sort()

        for index in keys:
            results.append(output_dict[index])

        return results

    # ================= DATALOADER =================

    def get_dataloaders(
        self,
        indices,
        input_texts,
        batch_size
    ):

        data_obj = IndicBERT_Data(indices, input_texts)

        dl = torch.utils.data.DataLoader(
            data_obj,
            batch_size=batch_size,
            shuffle=False
        )

        return dl

    # ================= PREDICT =================

    def predict(self, input):

        input_list = [input]

        return self.batch_predict(input_list, 1)

    # ================= BATCH PREDICT =================

    def batch_predict(self, input_list, batch_size):

        output_dict = {}

        roman_inputs = []
        native_inputs = []

        for index, input in enumerate(input_list):

            if self.char_percent_check(input) > self.input_threshold:
                roman_inputs.append((index, input))
            else:
                native_inputs.append((index, input))

        output_dict = self.native_inference(
            native_inputs,
            output_dict
        )

        output_dict = self.roman_inference(
            roman_inputs,
            output_dict,
            batch_size
        )

        results = self.post_process(output_dict)

        return results

    # ================= LANGUAGE CONVERSION =================

    def convert_label(self, label):

        mapping = {

            "asm_Beng": "as",
            "asm_Latn": "as",

            "ben_Beng": "bn",
            "ben_Latn": "bn",

            "brx_Deva": "brx",
            "brx_Latn": "brx",

            "doi_Deva": "doi",

            "guj_Gujr": "gu",
            "guj_Latn": "gu",

            "hin_Deva": "hi",
            "hin_Latn": "hi",

            "kan_Knda": "kn",
            "kan_Latn": "kn",

            "kas_Arab": "ks",
            "kas_Deva": "ks",
            "kas_Latn": "ks",

            "kok_Deva": "kok",
            "kok_Latn": "kok",

            "mai_Deva": "mai",
            "mai_Latn": "mai",

            "mal_Mlym": "ml",
            "mal_Latn": "ml",

            "mni_Beng": "mni",
            "mni_Meti": "mni",
            "mni_Latn": "mni",

            "mar_Deva": "mr",
            "mar_Latn": "mr",

            "nep_Deva": "ne",
            "nep_Latn": "ne",

            "ori_Orya": "or",
            "ori_Latn": "or",

            "pan_Guru": "pa",
            "pan_Latn": "pa",

            "san_Deva": "sa",
            "san_Latn": "sa",

            "sat_Olch": "sat",

            "snd_Arab": "sd",
            "snd_Latn": "sd",

            "tam_Tamil": "ta",
            "tam_Latn": "ta",

            "tel_Telu": "te",
            "tel_Latn": "te",

            "urd_Arab": "ur",
            "urd_Latn": "ur",

            "eng_Latn": "en"
        }

        return mapping.get(label, "en")

    # ================= SIMPLE DETECT =================

    def detect(self, text):

        result = self.batch_predict([text], 1)[0]

        raw_lang = result[1]

        detected_lang = self.convert_label(raw_lang)

        text_lower = text.lower()

        # Romanized Hindi conversational markers

        romanized_hindi_markers = {

            "hai",
            "hun",
            "hoon",
            "mera",
            "tera",
            "tum",
            "kya",
            "kyu",
            "kyon",
            "kaise",
            "acha",
            "accha",
            "kal",
            "ghar",
            "raha",
            "rahi",
            "jaa",
            "jaa",
            "milte",
            "baad",
            "kaha",
            "kahaan",
            "rahe",
            "aur"
        }

        words = set(text_lower.split())

        marker_matches = len(
            words.intersection(
                romanized_hindi_markers
            )
        )

        # English sentence detection
        
        english_words = {

            "hello",
            "how",
            "are",
            "you",
            "please",
            "project",
            "deadline",
            "report",
            "meeting",
            "tomorrow",
            "backend",
            "frontend"
        }

        english_matches = len(
            words.intersection(
                english_words
            )
        )

        
        # Strong English override

        if (

            english_matches >= 2

            and marker_matches == 0

        ):

            return "en"

        # Romanized Hindi override

        if (

            marker_matches >= 1

            and detected_lang in [

                "pa",
                "ur",
                "or",
                "ta",
                "en",
                "kok"
            ]

        ):

            return "hi"

        return detected_lang
#!/usr/bin/env python3
# coding: utf-8
import os
import ahocorasick

class QuestionClassifier:
    def __init__(self):
        cur_dir = '/'.join(os.path.abspath(__file__).split('/')[:-1])
        #feature word path
        self.disease_path = os.path.join(cur_dir, 'dict/disease.txt')
        self.department_path = os.path.join(cur_dir, 'dict/department.txt')
        self.check_path = os.path.join(cur_dir, 'dict/check.txt')
        self.drug_path = os.path.join(cur_dir, 'dict/drug.txt')
        self.food_path = os.path.join(cur_dir, 'dict/food.txt')
        self.producer_path = os.path.join(cur_dir, 'dict/producer.txt')
        self.symptom_path = os.path.join(cur_dir, 'dict/symptoms.txt')
        self.deny_path = os.path.join(cur_dir, 'dict/deny.txt')
        # Load feature words
        self.disease_wds= [i.strip() for i in open(self.disease_path,encoding="utf-8") if i.strip()]
        self.department_wds= [i.strip() for i in open(self.department_path,encoding="utf-8") if i.strip()]
        self.check_wds= [i.strip() for i in open(self.check_path,encoding="utf-8") if i.strip()]
        self.drug_wds= [i.strip() for i in open(self.drug_path,encoding="utf-8") if i.strip()]
        self.food_wds= [i.strip() for i in open(self.food_path,encoding="utf-8") if i.strip()]
        self.producer_wds= [i.strip() for i in open(self.producer_path,encoding="utf-8") if i.strip()]
        self.symptom_wds= [i.strip() for i in open(self.symptom_path,encoding="utf-8") if i.strip()]
        self.region_words = set(self.department_wds + self.disease_wds + self.check_wds + self.drug_wds + self.food_wds + self.producer_wds + self.symptom_wds)
        self.deny_words = [i.strip() for i in open(self.deny_path,encoding="utf-8") if i.strip()]
        # contruction
        self.region_tree = self.build_actree(list(self.region_words))
        # build dictionary
        self.wdtype_dict = self.build_wdtype_dict()
        # question words
        self.symptom_qwds = ['symptom', 'syndrome','symptoms', 'sign', 'manifestation', 'sickness', 'disorder']
        self.disease_qwds = ['What disease', "what's the disease" , "what's wrong", 'what happened']
        self.cause_qwds = ['reason', 'cause', 'why', 'how', 'Will', 'how can',  'will cause', 'causes','source','ground','root']
        self.acompany_qwds = ['complications', 'concurrent', 'together', 'Co-occurrence','come along','complications', 'concurrent', 'together', 'Co-occurrence','comes along']
        self.food_qwds = ['Diet', 'drinking', 'eating', 'foods', 'food', 'meal', 'drinking', 'dishes', 'taboo', 'supplements', 'health products', 'recipes', ' Recipes', 'Edible', 'Food', 'Supplements','Diet', 'drinking', 'eat',  'food', 'meal', 'drink', 'vegetables','supplements', 'health products', ' Recipes', 'Edible',  'Supplements']
        self.drug_qwds = ['Medicine', 'medicine', 'medication', 'capsule', 'oral solution', 'flame tablet', 'what medicine to eat','drugs to cure','Medicine','medication', 'capsule', 'oral solution', 'flame tablets','tablets','drugs','antibiotic','remedy','dose','prescription','vaccine']
        self.prevent_qwds = ['prevent', 'prevent', 'resist', 'resist', 'prevent', 'avoid', 'escape', 'avoid', 'avoid', 'escape', 'Avoid', 'How can I not',
                              'How can you not', 'How can you not', 'How can you not', 'How can you not', 'How can you not','Prevent','resist','avoid', 'escape', 'Avoid', 'How can I not',  'How Just not', 'How not', 'How not to', 'Why not','avoidance','block','counter','limit']
        self.lasttime_qwds = ['period', 'how long', 'time', 'days', 'years',  'hours', 'previously']
        self.cureway_qwds = ['cure','Cure', 'treatment', 'method', 'therapy','remedy','recovery',  'remove']
        self.cureprob_qwds = ['probability', 'cured', ' likely', 'several percent', 'proportion', 'possibility']
        self.easyget_qwds = ['prone','Susceptible population', 'susceptible to infection', 'who is affected easily', 'infected', 'got']
        self.check_qwds = ['what kind of tests','check', 'check item', 'find out', 'check', 'tests','out', 'verify','reports','look into']
        self.belong_qwds = ['Belongs','department', 'belongs to', 'department','Department']
        self.cure_qwds = ['What is the treatment',  'what is the cure', 'what is the indication', 'what is the indication', 'what is the use','how to cure', 'usefulness' , 'purpose',
                           "what's good", 'need', 'to']

        self.sicknotice_qwds = ['Attention', 'concern', 'care', 'caution', 'watch out', 'care']
        self.negation_qwds = ['should not','avoid','beware',"Don't","should",'prevent','prohibit','neglect','less','dont']

        print('model init finished ......')

        return

    '''classification main function'''
    def classify(self, question):
        data = {}
        medical_dict = self.check_medical(question)
        if not medical_dict:
            return {}
        data['args'] = medical_dict
        #Collect the entity types involved in the question
        types = []
        for type_ in medical_dict.values():
            types += type_
        question_type = 'others'

        question_types = []

        # symptoms
        if self.check_words(self.symptom_qwds, question) and ('disease' in types):
            question_type = 'disease_symptom'
            question_types.append(question_type)

        # if self.check_words(self.symptom_qwds, question) and ('symptom' in types):
        #     question_type = 'symptom_disease'
        #     question_types.append(question_type)

        # cause
        if self.check_words(self.cause_qwds, question) and ('disease' in types):
            question_type = 'disease_cause'
            question_types.append(question_type)

            
        # accompany
        if self.check_words(self.acompany_qwds, question) and ('disease' in types):
            question_type = 'disease_acompany'
            question_types.append(question_type)

        # recommended food
        if self.check_words(self.food_qwds, question) and 'disease' in types:
            deny_status = self.check_words(self.negation_qwds, question)
            if deny_status:
                question_type = 'disease_not_food'
            else:
                question_type = 'disease_do_food'
            question_types.append(question_type)

        #Known Foods Find Diseases
        if self.check_words(self.food_qwds+self.cure_qwds, question) and 'food' in types:
            deny_status = self.check_words(self.negation_qwds, question)
            if deny_status:
                question_type = 'food_not_disease'
            else:
                question_type = 'food_do_disease'
            question_types.append(question_type)

        # Recommended Drugs
        if self.check_words(self.drug_qwds, question) and 'disease' in types:
            question_type = 'disease_drug'
            question_types.append(question_type)

        # what medicine cures
        if self.check_words(self.cure_qwds, question) and 'drug' in types:
            question_type = 'drug_disease'
            question_types.append(question_type)

        # disease acceptance test
        if self.check_words(self.check_qwds, question) and 'disease' in types:
            question_type = 'disease_check'
            question_types.append(question_type)

        # Known inspection items to check corresponding diseases
        if self.check_words(self.check_qwds+self.cure_qwds, question) and 'check' in types:
            question_type = 'check_disease'
            question_types.append(question_type)

        #symptom defense
        if self.check_words(self.prevent_qwds, question) and 'disease' in types:
            question_type = 'disease_prevent'
            question_types.append(question_type)

        # disease medical cycle
        if self.check_words(self.lasttime_qwds, question) and 'disease' in types:
            question_type = 'disease_lasttime'
            question_types.append(question_type)

        # disease treatment
        if self.check_words(self.cureway_qwds, question) and 'disease' in types:
            question_type = 'disease_cureway'
            question_types.append(question_type)

        # Possibility of disease cure
        if self.check_words(self.cureprob_qwds, question) and 'disease' in types:
            question_type = 'disease_cureprob'
            question_types.append(question_type)

        # disease-prone population
        if self.check_words(self.easyget_qwds, question) and 'disease' in types :
            question_type = 'disease_easyget'
            question_types.append(question_type)

        # If no relevant external query information is found,then return the description information of the disease
        if question_types == [] and 'disease' in types:
            question_types = ['disease_desc']

        # If no relevant external query information is found, then return the description information of the disease
        # if question_types == [] and 'symptom' in types:
        #     question_types = ['symptom_disease']

        # Merge multiple classification results and assemble them into a dictionary
        data['question_types'] = question_types

        return data

    '''The type corresponding to the constructed word'''
    def build_wdtype_dict(self):
        wd_dict = dict()
        for wd in self.region_words:
            wd_dict[wd] = []
            if wd in self.disease_wds:
                wd_dict[wd].append('disease')
            if wd in self.department_wds:
                wd_dict[wd].append('department')
            if wd in self.check_wds:
                wd_dict[wd].append('check')
            if wd in self.drug_wds:
                wd_dict[wd].append('drug')
            if wd in self.food_wds:
                wd_dict[wd].append('food')
            if wd in self.symptom_wds:
                wd_dict[wd].append('symptom')
            if wd in self.producer_wds:
                wd_dict[wd].append('producer')
        return wd_dict

    '''actree'''
    def build_actree(self, wordlist):
        actree = ahocorasick.Automaton()
        for index, word in enumerate(wordlist):
            actree.add_word(word, (index, word))
        actree.make_automaton()
        return actree

    '''checking medical'''
    def check_medical(self, question):
        region_wds = []
        for i in self.region_tree.iter(question):
            wd = i[1][1]
            region_wds.append(wd)
        stop_wds = []
        for wd1 in region_wds:
            for wd2 in region_wds:
                if wd1 in wd2 and wd1 != wd2:
                    stop_wds.append(wd1)
        final_wds = [i for i in region_wds if i not in stop_wds]
        final_dict = {i:self.wdtype_dict.get(i) for i in final_wds}

        return final_dict

    '''check words'''
    def check_words(self, wds, sent):
        for wd in wds:
            if wd in sent:
                return True
        return False


if __name__ == '__main__':
    handler = QuestionClassifier()
    while 1:
        question = input('input an question:')
        data = handler.classify(question)
        print(data)
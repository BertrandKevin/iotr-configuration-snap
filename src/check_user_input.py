#!/usr/bin/python

def question_and_verification(question):
        answer = ""

        while answer != "y" and answer != "n":
                answer = input(question)
                answer = answer.lower()

        return answer

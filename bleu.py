import codecs
import functools
import math
import operator
import os
import sys


def getCandidateList(candidateList, referenceList, gramCount):
    listNGramsCandidate = []
    listNGramsReference = []
    listNGramsReferenceLength = []

    for index, eachLine in enumerate(candidateList):
        eachSentence = eachLine.strip().split()
        eachLineNGrams = {}
        for eachWordIndex in range(len(eachSentence) - gramCount + 1):
            ngram = ' '.join(
                eachSentence[eachWordIndex:eachWordIndex + gramCount]).lower()
            if ngram not in eachLineNGrams:
                eachLineNGrams[ngram] = 1
            else:
                eachLineNGrams[ngram] += 1

        listNGramsCandidate.append(eachLineNGrams)
        eachNGramReference, eachNGramReferenceLength = getReferenceList(
            index, referenceList, gramCount)
        listNGramsReference.append(eachNGramReference)
        listNGramsReferenceLength.append(eachNGramReferenceLength)
    return listNGramsCandidate, listNGramsReference, listNGramsReferenceLength

def getReferenceList(index, referenceList, gramCount):
    eachNGramReference = []
    eachNGramReferenceLength = []

    for reference in referenceList:
        eachWord = reference[index].strip().split()
        eachNGramReferenceLength.append(len(eachWord))
        eachLineNGrams = {}
        for eachWordIndex in range(len(eachWord) - gramCount + 1):
            ngram = ' '.join(
                eachWord[eachWordIndex:eachWordIndex + gramCount]).lower()
            if ngram not in eachLineNGrams:
                eachLineNGrams[ngram] = 1
            else:
                eachLineNGrams[ngram] += 1
        eachNGramReference.append(eachLineNGrams)

    return eachNGramReference, eachNGramReferenceLength


def getRefCounts(candidate, reference, referenceLength, candidateLength):
    count = 0
    for eachKey in candidate.keys():
        eachKeyCount = candidate[eachKey]
        eachKeyMax = 0
        for eachReference in reference:
            if eachKey in eachReference:
                eachKeyMax = max(eachKeyMax, eachReference[eachKey])
        eachKeyCount = min(eachKeyCount, eachKeyMax)
        count += eachKeyCount

    least_diff = abs(candidateLength - referenceLength[0])
    bestValue = referenceLength[0]
    for eachReferenceLength in referenceLength:
        if abs(candidateLength - eachReferenceLength) < least_diff:
            least_diff = abs(candidateLength - eachReferenceLength)
            bestValue = eachReferenceLength
    return count, bestValue

def main():
    candidateList = ""
    referenceList = []
    for index, arg in enumerate(sys.argv):
        if index == 1:
            with open(arg, encoding='utf8') as text_file:
                candidate_text_list = text_file.read().splitlines()
            candidateList = [x.strip() for x in candidate_text_list]

        elif index == 2:
            if (os.path.isfile(arg)):
                with open(arg, encoding='utf8') as text_file:
                    reference_text_list = text_file.readlines()
                referenceList.append([x.strip() for x in reference_text_list])
            else:
                for eachFile in os.listdir(arg):
                    eachFile = os.path.join(arg, eachFile)
                    with open(eachFile, encoding='utf8') as text_file:
                        reference_text_list = text_file.readlines()
                    referenceList.append(
                        [x.strip() for x in reference_text_list])

    precisions = []
    for gramCount in range(1, 5):
        listNGramsCandidate, listNGramsReference, listNGramsReferenceLength = getCandidateList(
            candidateList, referenceList, gramCount)
        candref_count = 0
        count = 0
        refCount = 0
        candCount = 0
        for i in range(len(listNGramsCandidate)):
            cand_sentence = candidateList[i]
            words = cand_sentence.strip().split()
            candRefTemp, refCountTemp = getRefCounts(listNGramsCandidate[i], listNGramsReference[i], listNGramsReferenceLength[i], len(listNGramsCandidate[i]))
            candref_count += candRefTemp
            refCount += refCountTemp
            count += (len(words) - gramCount + 1)
            candCount += len(words)

        if candref_count == 0:
            pr = 0
        else:
            pr = float(candref_count) / count

        print (str(candref_count) + " : " + str(count) + " : " + str(candCount) + " : " + str(refCount))

        if candCount > refCount:
            penalty = 1
        else:
            penalty = math.exp(1 - (float(refCount) / candCount))

        precisions.append(pr)
        print(str(penalty) + " : " + str(precisions))
        print (functools.reduce(operator.mul, precisions))
        print ()
    bleu = (functools.reduce(operator.mul, precisions))**(1.0 / len(precisions)) * penalty
    print(bleu)
    outFile = open('bleu_out.txt', 'w')
    outFile.write(str(bleu))
    outFile.close()

if __name__ == '__main__':
    main()
import re
import itertools

testNameConvention = "{measurement type}_batch_{batch number}"
testItemList = ["cytokine_batch_1", "cytokine_batch_2", "mrna_batch_1", "mrna_batch_2", "mrna_batch_3",]

def get_descriptions(testNameConvention,testItemList):

    nameConventionExplanatoryList = re.findall('{(.+?)}', testNameConvention) # list of items enclosed in curly braces
    print(nameConventionExplanatoryList)

    if nameConventionExplanatoryList: # check if user added any naming convention explanatory values in the correct format (between curly braces); if yes, continue, if no, print informative message and return

        nameConventionAllList = re.split('[/{/}]', testNameConvention)
        nameConventionAllList = [l for l in nameConventionAllList if l] # list of items delimited by curly braces (either direction)
        print(nameConventionAllList)

        nameOnlyOneExplanatory = False # set default value as false
        # check for delimiters between naming convention explanatory variables - need these to parse filenames to descriptions
        # if length of two lists is same then no delimiters between explanatory values exist, but if list is length one this is handle-able  
        if len(nameConventionAllList) == len(nameConventionExplanatoryList):
            if len(nameConventionAllList) == 1:
                nameOnlyOneExplanatory = True
            else:
                print("Naming convention explanatory values are not separated by a delimiter in your file name convention. Please add delimiters between file naming convention explanatory values in your filenames. Snake case as a delimiter is not currently supported but will be soon.")
                return

        if not nameOnlyOneExplanatory:
            noDelim = 0
            for idx, l in enumerate(nameConventionAllList):
                beforeVal = None
                afterVal = None
                if l in nameConventionExplanatoryList:
                    if idx != len(nameConventionAllList) - 1: # if not last element, get element after current element  
                        afterVal = nameConventionAllList[idx + 1]
                    if idx != 0: # if not first element, get element before current element  
                        beforeVal = nameConventionAllList[idx - 1]
            
                    if afterVal:
                        if afterVal in nameConventionExplanatoryList:
                            noDelim += 1
                            print(l," and ",afterVal," naming convention explanatory values are not separated by a delimiter in your file name convention. Please add delimiters between file naming convention explanatory values in your filenames. Snake case as a delimiter is not currently supported but will be soon.")

                    if beforeVal:
                        if beforeVal in nameConventionExplanatoryList:
                            noDelim += 1
                            print(beforeVal," and ",l," naming convention explanatory values are not separated by a delimiter in your file name convention. Please add delimiters between file naming convention explanatory values in your filenames. Snake case as a delimiter is not currently supported but will be soon.")
  
            if noDelim > 0:
                print("Naming convention explanatory values are not separated by a delimiter in your file name convention. Please add delimiters between file naming convention explanatory values in your filenames. Snake case as a delimiter is not currently supported but will be soon.")
                return


        allFilesDescribeList = [] 

        for i in testItemList:
        
            oneFileDescribeList = []  

            if nameOnlyOneExplanatory:
                oneFileDescribe = nameConventionAllList[0] + ": " + i
            else: 
            
                for idx, l in enumerate(nameConventionAllList):
                    beforeVal = None
                    beforeValSplit = None
                    afterVal = None
                    afterValSplit = None
                    if l in nameConventionExplanatoryList:
                        if idx != len(nameConventionAllList) - 1: # if not last element, get element after current element  
                            afterVal = nameConventionAllList[idx + 1]
                        if idx != 0: # if not first element, get element first current element  
                            beforeVal = nameConventionAllList[idx - 1]
            
                        if afterVal:
                            if afterVal in i:
                                afterValSplit = i.split(afterVal)
                        
                            else:
                                print("the file named ", i, " does not conform to the specified naming convention. It does not contain the string ",afterVal," as specified by the applied naming convention.")
                                continue

                        if beforeVal:
                            if beforeVal in i:
                                beforeValSplit = i.split(beforeVal)
                        
                            else:
                                print("the file named ", i, " does not conform to the specified naming convention. It does not contain the string ",beforeVal," as specified by the applied naming convention.")
                                continue

                        if ((not afterValSplit) and (not beforeValSplit)):
                            print("the file named ", i, " does not conform to the specified naming convention. It does not contain string(s) specified by the applied naming convention. Exiting check of this file.")
                            break

                        if ((afterValSplit) and (not beforeValSplit)):
                            myVal = afterValSplit[0]

                        if ((not afterValSplit) and (beforeValSplit)):
                            myVal = beforeValSplit[1]
                    
                        if ((afterValSplit) and (beforeValSplit)):
                            myVal = afterValSplit[0]
                            myVal = myVal.split(beforeVal)[1]
                    
                        myDescribe = l + ": " + myVal
                        oneFileDescribeList.append(myDescribe)   
            
                oneFileDescribe = '\n'.join(oneFileDescribeList)
                print(oneFileDescribe)    
            
            allFilesDescribeList.append(oneFileDescribe) 
            print(allFilesDescribeList)    

get_descriptions(testNameConvention = testNameConvention, testItemList = testItemList)   
            
           





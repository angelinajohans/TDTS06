
import re

#Contains the scanning/filtering functions
class uglyWordsFinder:

    #This function checks whether the input argument string contains an image 
    #and subsequently does not need to be investigated or does not contain an image
    #and should be investigated.
    #Contains image returs False
    #Does not contain image returns True
    def image(self, request): #or just url?
        print('In the need_to_investigate function')
        divided = request.split('\r\n')
        
        for i in divided:
            #print(len(divided))
            #print('In the if in need_to_invest.')
            #print('Content in line:',i)
            TypeIndex = divided.index(i)
            print('This is the TypeIndex variable:',TypeIndex)
            pos = divided[TypeIndex].find('Content-Type')
            print('Content-type in position',pos)
            
            if pos != -1:
                line = divided[TypeIndex]
                print('Line: \n', line)
                pic = line.find('text')
                if pic != -1:
                    print('THIS IS NOT AN IMAGE')
                    return False
                else:
                    return True
            else:
                continue

        return False


    def acceptable_data(self, request):
        forbidden_words = ['[Bb]ritney ?[Ss]pears', '[Pp]aris ?[Hh]ilton', '[Ss]ponge[Bb]ob']#,'[Mm]otala']
         
        #For every item in forbidden words list look for the word in the object of interest.
        #If found return False; not acceptable, if not found continue with next.
        #If no words are found, return True; acceptabl
        for i in forbidden_words:
            found_words = re.findall(i,request)
            print('THIS IS NOT AN IMAGE AND WE ARE IN DATA CONTROL FUNCTION')
            if found_words != []:
                print('The object is dirty')
                return False
            else:
                print('In continue in if in acceptable_data')
                continue
            
        print('The object is clean\n')
        return True
    
    
    
        # pic_formats = ['.tif','.tiff','.bmp','.jpg','.jpeg','.gif','.png','.eps', '.ico']
        
        # #For every item in string list pic_formats
        # #look for the format keyword in the input string
        # for i in pic_formats:
        #     exist = request.find(i)
        #     print('The uglyWordsFinder is searching through the content and exist for',i,'is:',exist)
            
        #     #If the image format keyword is not found, continue with next keyword
        #     #else (if the keyeord is found) return True; needs to be investagated
        #     if exist != -1:
        #         print('The object does not need to be investigated')
        #         self.picture = 1
        #         return False
        #     else:
        #         continue
        # print('The object needs to be investigated')
        # self.picture = 0
        # return True
        
    #This function check if the object of interest contains any forbidden words.
    #If contains fobidden words, it is unacceptable and returns False
    #If does not contain forbidden words, it is acceptable and returns True
    # def acceptable(self, obj_of_interest):
    #     forbidden_words = ['[Bb]ritney ?[Ss]pears', '[Pp]aris ?[Hh]ilton', '[Ss]ponge[Bb]ob']#,'[Mm]otala']
        
    #     #If the object of interest needs to be investigated
    #     #enter search for forbidden words
    #     #else (if no need for investigation) return True; acceptable
    #     if self.need_to_investigate(obj_of_interest):
            
    #         #For every item in forbidden words list look for the word in the object of interest.
    #         #If found return False; not acceptable, if not found continue with next.
    #         #If no words are found, return True; acceptable
    #         for i in forbidden_words:
    #             found_words = re.findall(i,obj_of_interest)
    #             if found_words != []:
    #                 print('The object is dirty')
    #                 return False
    #             else:
    #                 continue
    #         print('The object is clean\n')
    #         return True
    #     else:
    #         print('The object is clean')
    #         return True
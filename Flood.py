import csv
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

#Creates class for each Line
class Line:
        
    def __init__(self,x1,y1,x2,y2,m=None,c=None,direction=None):

        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.m = m
        self.c = c
        self.direction = direction
        
        if direction == None:
            self.direction = self.isStraightLine()

        if self.direction == 'd' and self.m == None:
                
            #Finds gradient
            self.m = (y1-y2)/(x1-x2)

            #Finds y intersect
            self.c = y1-(self.m*x1)
        else:
            self.m = m
            self.c = c

    def isStraightLine(self):

        if self.x1 - self.x2 == 0:
            #Vertical Line
            return 'v'
        elif self.y1 -self.y2 == 0:
            #Horizontal Line
            return 'h'
        else:
            return 'd'
        
    #Run the maths to determine wheter a line intersects. returns int
    def doesLineIntersect(self,xPlot,yPlot):

        xPlot = float(xPlot)
        yPlot = float(yPlot)
        
        if self.withinBoundingBox(xPlot,yPlot):
            if self.direction == 'v':
                #How to deal with a vertical line
                if self.intersectStraightLine(yPlot,self.y1,self.y2,xPlot,self.x1):
                    #Do not count intersections twice
                    if self.x1 == xPlot or self.y1 == yPlot:
                        return 0
                    else:
                        print("%s,%s to %s,%s intersects" % (self.x1,self.y1,self.x2,self.y2))
                        return 1
                else:
                    return 0
            elif self.direction == 'h':
                 return 0
            else:
                #How to deal with a line with a gradient
                
                self.xIntersect = self.findXintersect(yPlot)
                if self.xIntersect < xPlot:
                    #Does not count intersections twice
                    if self.x1 == xPlot or self.y1 == yPlot:
                        return 0
                    else:
                        print("%s,%s to %s,%s intersects" % (self.x1,self.y1,self.x2,self.y2))
                        return 1
                else:
                    return 0
        else:
            return 0

    #Finds whether a point is on the border of a floodZone
    def isPointOnLine(self,xPlot,yPlot):
        
        if self.direction == 'h':
            if self.y1 == yPlot:
                if xPlot <= self.largeNumber(self.x1,self.x2) and xPlot >= self.smallNumber(self.x1,self.x2):
                    return True
        elif self.direction == 'v':
            if self.x1 == xPlot:
                if xPlot <= self.largeNumber(self.x1,self.x2) and xPlot >= self.smallNumber(self.x1,self.x2):
                    return True
        elif self.direction == 'd':
            #How do we know?
            if xPlot == self.findYIntersect(float(xPlot)) and yPlot == self.findXIntersect(float(yPlot)):
                return True
            pass
    

    #Find whether the point is within the bounding box of the line
    def withinBoundingBox(self,xPlot,yPlot):

        if self.y1-self.y2 == 0:
            if xPlot <= self.largeNumber(self.x1,self.x2) and xPlot >= self.smallNumber(self.x1,self.x2):
                return True
        else:
            if yPlot <= self.largeNumber(self.y1,self.y2) and yPlot >= self.smallNumber(self.y1,self.y2):
                return True

    #Find whether the point crosses a line with no gradient
    def intersectStraightLine(self,aIntersect,a1,a2,aPlot,b1):
        
        if aIntersect <= self.largeNumber(a1,a2) and aIntersect >= self.smallNumber(a1,a2):
            if aPlot > b1:
                return True

    # If x is the same then y equals xIntersect
    def findXintersect(self,yPlot):
        
         xIntersect = (yPlot - self.c) / self.m

         return xIntersect

    #If y is the same then x equals yIntersect
    def findYIntersect(self,xPlot):

        yIntersect = (self.m * xPlot) + self.c

        return yIntersect
    
    #Find the largest number
    def largeNumber(self,a,b):

        if a > b:
            return a
        else:
            return b

    #Find the smallest number
    def smallNumber(self,a,b):

        if a < b:
            return a
        else:
            return b

#Creates Class for each Property
class PropertyItem:

    def __init__(self,addressLine1,postCode,x,y,hawkeyeRAG,floodZones=None):

            self.addressLine1 = addressLine1
            self.postCode = postCode
            self.x = x
            self.y = y
            self.hawkeyeRAG = hawkeyeRAG
            self.floodZones = floodZones

class CompletePropertyData:
    
    #Creates an Array from a pipe delimted Hawkeye download
    def __init__(self,fileName):
        
        self.companyPropertyLocation = []
        i = 0
        
        with open(fileName, 'r') as csvfile:
            collectData = csv.reader(csvfile, delimiter='|')
            for row in collectData:
                if i > 0:
                    propertyInformation = PropertyItem(row[0],row[1],row[2],row[3],row[4])
                    self.companyPropertyLocation.append(propertyInformation)
                else:
                    i+=1
                    
    #Checks Property Array against FloodZone
    def checkPropertiesAgainstFloodZones(self,floodZone,floodTitle = None):
        
        for item in self.companyPropertyLocation:

            intersectionCount = 0
            
            #Checks against Hawykeye
            if item.hawkeyeRAG != "Green":
                i=0 
                for XY in floodZone:
                    if i == 0:
                        firstCoord = XY
                        i +=1
                    elif i == 1:
                        secondCoord = XY
                        line = Line(firstCoord[0],firstCoord[1],secondCoord[0],secondCoord[1])
                        if line.isPointOnLine(item.x,item.y):
                            intersectionCount = 0
                            item.floodZones = floodTitle
                            break
                        intersectionCount = intersectionCount + line.doesLineIntersect(item.x,item.y)
                        i += 1
                    else:
                        firstCoord = secondCoord
                        secondCoord = XY
                        line = Line(firstCoord[0],firstCoord[1],secondCoord[0],secondCoord[1])
                        if line.isPointOnLine(item.x,item.y):
                            intersectionCount = 0
                            item.floodZones = floodTitle
                            break
                        line = Line(firstCoord[0],firstCoord[1],secondCoord[0],secondCoord[1])
                        intersectionCount = intersectionCount + line.doesLineIntersect(item.x,item.y)
                print("intersection count is %s" % (intersectionCount,))       
                if intersectionCount % 2 == 1:
                    item.floodZones = floodTitle
                    intersectionCount = 0
                print(item.x,item.y)

        return self.companyPropertyLocation


class CompileAndSendEmails():

    def __init__(self,propertyData,customerName,companyName):

        self.emailString = r"""<html><head><style>body { font-family: Calibri !important; }</style></head><body style='font-
            family:Calibri;background-color:#E0E6E6;'><table width='800' border='0' align='center' style='border:0px;backgrond
            -color:#fff;'><tr><td width='100%' bgcolor='#fff' style='background-color:#fff;'><p align='right' style='margin:5px
            ;font-size:14px;'></p></td></tr><tr><td width='100%' bgcolor='#ffd900' height='80' align='center'><table width='100%
            '><tr><td width='22%' align='right'><img src='' width='150' alt
            ='Aviva' /></td><td style='font-size:28px;font-family:Calibri;padding-top:12px;' width='78%'>&nbsp;Flood Prevention</td></tr
            ></table></td></tr><tr><td style='background-color:#fff;'><table width='95%'
            align='center'><tr><td style='font-size:14px;'><p><br />To """ + customerName + """,</p><p>Please be aware that
            the following properties are located within a current flood alert. For more information on the severity and
            location of the flood, please visit the <a href='https://flood-warning-information.service.gov.uk/5-day-flood-risk
            '>Environmental Agency website</a>.</p><table border='1' style='font-size:14px;' width='100%'><tr><td width='25%'>
            <strong>Flood Severity</strong></td><td width='65%'><strong>Property Address</strong></td><td width='10%' align='
            center'><strong>Details</strong></td></tr>"""                              
            
        emailStringProperties = ""
        toEmailFlag = False
        self.emailStringEnd = r"""</table><p>Further information on how you can protect your property <a href='#'>Flood Risk Management Checklist</a>.</p><p>Kind Regards,<br />
                                Flood Prevention<br />&nbsp;</p></td></tr></table><br/></td></tr></table></body></html>"""
        
        for x in propertyData:
            print (x.floodZones)
            if x.floodZones != None:
                toEmailFlag = True
                emailStringProperties = r"%s<tr><td>%s</td><td>%s</td><td><a href='https://flood-warning-information.service.gov.uk/warnings?location=%s'>View Details</a></td></tr>" % (emailStringProperties,"A Bad Flood",
                                                                                           x.addressLine1,x.postCode)

        if toEmailFlag:
            self.emailString = self.emailString + emailStringProperties + self.emailStringEnd
            self.sendEmail(emailReceiver,companyName)

    def sendEmail(self,toAddress,companyName):

        print(self.emailString)
        
        from_address = 'email@email.com'
        to_address = toAddress
                    
        msg = MIMEMultipart()
        msg['From']=from_address
        msg['To']=to_address
        msg['Subject']='Flood Prevention Alert for ' + companyName   
                
        msg.attach(MIMEText(self.emailString,'html'))
    
        server = smtplib.SMTP('015-smtp-out.aviva.com')
        text=msg.as_string()
        server.sendmail(from_address,to_address,text)

floodZoneTest = [(-0.305656, 50.821889),
	(-0.307402, 50.824826),
	(-0.303825, 50.826263),
	(-0.296029, 50.827872),
	(-0.294971, 50.827058),
	(-0.291766, 50.827718),
	(-0.290207, 50.827546),
	(-0.288090, 50.825025),
	(-0.305656, 50.821889)]

#floodZoneTest = [(52,45),(45,12),(0,4),(78,545),(100,90),(100,500),(112,300),(101,352),(130,111),(140,600),(2,612),(150,698),(170,2),(75,45),(77,325),(76,425),(56,2),(51,300),(52,45)]

companyName = "Your Awesome Business"
fileName = "Your Awesome Business.csv"
emailReceiver = "email@email.com"
floodTitle = "Caution Possible Flooding"
customerName = "Mr Cutomer"


def main():

    someProperties = CompletePropertyData(fileName)
    someProperties = someProperties.checkPropertiesAgainstFloodZones(floodZoneTest,floodTitle)

    emailBody = CompileAndSendEmails(someProperties,customerName,companyName)


    

        

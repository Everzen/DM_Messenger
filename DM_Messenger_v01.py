from PySide import QtCore, QtGui
import sys
import copy
import qdarkstyle
import json
from slackclient import SlackClient



#Tempory development token to talk to SVFX-DND-ADVENTURE.slack.com - This validates user DM sending direct messages too! 

jsonFile = 'resources\MessengerData_SVFX.json'
# jsonFile = 'resources\MessengerData_DnKnee.json'
# jsonFile = 'resources\MessengerData_Illumria.json'

statementCategories = {"CommonStatements" : "Common Statements", "RelativeStatements" : "Relative Statements", "Questions" : "Questions", "QuestStatements": "Quest Specific", "voices" : "Voices", "regardings": "Regardings" }
# print ("Keys " + str(statementCategories.keys()))

tabColumnWidth = 405

def grabInfo(infoType):
    with open(jsonFile) as json_file:
            info = json.load(json_file)
            return info[infoType]

#Saving JSON
# import json
# with open('data.json', 'w') as fp:
#     json.dump(data, fp)


DMInfo = None

with open(jsonFile) as json_file:
    DMInfo = json.load(json_file)


##Grab the securtiy information from the Json file....
# slackdevToken = DMInfo["security"]
# slack_client = SlackClient(slackdevToken["DMToken"])


# print(str(DMInfo))

# print (" ----------------------------------------")

# DMInfo["voices"].append({"name" : "badger", "asUser" : 0})

# print(str(DMInfo))


# def saveJson():
#     with open(jsonFile, 'w') as json_file:
#         json.dump(DMInfo, json_file)




##############################DEFINE CLASSES TO HANDLE JSON############################
class Voice(object):
    def __init__(self):
        self.rawJson = None
        self.lwItem = None
    
    def getLWItem(self):
        return self.lwItem

    def setLWItem(self):
        newItem = QtGui.QListWidgetItem((self.rawJson["name"]))
        newItem.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsDragEnabled | QtCore.Qt.ItemIsDropEnabled)
        self.lwItem = newItem
        return newItem

    def set(self, statementJson):
        self.rawJson = statementJson
        self.setLWItem()

    def get(self):
        return self.rawJson

    def create(self):
        self.rawJson = {"asUser": 0, "name": "New Voice", "fade":0}
        self.setLWItem()

    def setStatementText(self, text):
        self.rawJson["name"] = text
        self.setLWItem()


class Regarding(object):
    def __init__(self):
        self.rawJson = None
        self.lwItem = None
    
    def getLWItem(self):
        return self.lwItem

    def setLWItem(self):
        newItem = QtGui.QListWidgetItem((self.rawJson["name"]))
        newItem.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsDragEnabled | QtCore.Qt.ItemIsDropEnabled)
        self.lwItem = newItem
        return newItem

    def set(self, statementJson):
        self.rawJson = statementJson
        self.setLWItem()

    def get(self):
        return self.rawJson

    def create(self):
        self.rawJson = {"fade": 0, "name": "New Character", "fade":0}
        self.setLWItem()

    def setStatementText(self, text):
        self.rawJson["name"] = text
        self.setLWItem()


class Statement(object):
    def __init__(self):
        self.rawJson = None
        self.lwItem = None
    
    def getLWItem(self):
        return self.lwItem

    def setLWItem(self):
        # print ("My Raw JSon is : " + str(self.rawJson))
        # print("My statemment is : " + str(self.rawJson["statement"]))
        newItem = QtGui.QListWidgetItem((self.rawJson["statement"]))
        newItem.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsDragEnabled | QtCore.Qt.ItemIsDropEnabled)
        self.lwItem = newItem
        return newItem

    def set(self, statementJson):
        self.rawJson = statementJson
        self.setLWItem()

    def get(self):
        return self.rawJson

    def create(self):
        self.rawJson = {"visible": 1, "statement": "Edit this statement", "fade":0}
        self.setLWItem()

    def setStatementText(self, text):
        self.rawJson["statement"] = text
        self.setLWItem()


class StatementList(object):
    def __init__(self, statementObj, categoryJson):
        self.rawJson = categoryJson
        self.statementObj = statementObj
        self.statements = self.collectStatements()


    def collectStatements(self):
        # print ("Category JSon : " + str(self.rawJson))
        newList = []
        for statementJson in self.rawJson:
            newStatement = self.statementObj()
            newStatement.set(statementJson)
            newList.append(newStatement)
        return newList

    def getStatements(self):
        return self.statements

    def setStatements(self, statementList):
        self.statements = statementList 
        self.getJson() #Call to update the Json

    def getJson(self):
        newJson = []
        for stateItem in self.statements: newJson.append(stateItem.get())
        self.rawJson = newJson
        return self.rawJson

    def add(self):
        newStatement = self.statementObj()
        newStatement.create() #Create a new addition
        self.statements.append(newStatement)

    def remove(self, index):
        del(self.statements[index])

    def populate(self):
        """This method rebuilds the treeWidgetList Items for the statement list since they get deleted by the LW.clear()"""
        for state in self.statements:
            state.setLWItem()


class DMInformation(object):
    def __init__(self, fileName, categories):
        self.fileName = fileName
        self.rawJson = self.loadJson()
        self.statementCategories = statementCategories
        self.categoryTitles = categories.keys()
        self.categoryDicts = self.collectStatementLists()

    def loadJson(self):
        with open(self.fileName) as json_file:
            return json.load(json_file)

    def getSecurity(self, dev = False):
        if dev:
            return self.rawJson["security"]["DevToken"]
        else:
            return self.rawJson["security"]["DMToken"]

    def save(self):
        with open(self.fileName, 'w') as json_file:
            json.dump(self.rawJson, json_file)

    def collectStatementLists(self):
        newStatementDic = {}
        list = None
        for cat in self.categoryTitles:
            if cat == "voices": list = StatementList(Voice, self.rawJson[cat])
            elif cat == "regardings": list = StatementList(Regarding, self.rawJson[cat])
            else: list = StatementList(Statement, self.rawJson[cat])
            newStatementDic.update({cat : list})
        print("New Statement Dictionaries " + str(newStatementDic["voices"].getStatements()))
        print("New Statement Dictionaries " + str(newStatementDic["regardings"].getStatements()))
        print(str(newStatementDic["regardings"].getStatements()[0].get()["name"]))
        print(str(newStatementDic["voices"].getStatements()[0].get()["name"]))
        return newStatementDic

    def getCategoryDict(self, category):
        return self.categoryDicts[category] 

    def setCategoryDict(self, category, statementList):
        self.categoryDicts[category] = statementList  #set the statement List
        self.rawJson[category] = statementList.getJson() # Update the main Json
        # print "The new JSon is : " + str(statementList.getJson())
        self.save() #Automatically save the Json

    def getRegardings(self):
        return self.rawJson["regardings"]

    def getVoices(self):
        return self.rawJson["voices"]

    def getPlayers(self):
        return self.rawJson["players"]




DMInfo = DMInformation(jsonFile, statementCategories)

slack_client = SlackClient(DMInfo.getSecurity())



class StatementsQLW(QtGui.QListWidget):
    def __init__(self, DMInfo, statementType, parent=None):
        super(StatementsQLW, self).__init__(parent)
        self.statementType = statementType
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu) #context menu for user data
        self.customContextMenuRequested.connect(self.userMenu)
        self.itemChanged.connect(self.editStatement)  #This is called when the enter key is pressed on the changing of the edited text
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDragDropMode(QtGui.QAbstractItemView.InternalMove)
        self.statementList = DMInfo.getCategoryDict(statementType)
        self.addItems() #Call method to populate Tree

    def getStatementList(self):
        return self.statementList

    def userMenu(self, position):
        menu = QtGui.QMenu()
        addStatement = "Nothing"
        editStatement = "Nothing"
        delStatement = "Nothing"

        option = "Statement"
        if self.statementType == "voices": option = "Voice"
        elif self.statementType == "regardings": option = "Character"
        if not (self.itemAt(position)): #Test right Click Position - have we hit an item
            addStatement = menu.addAction(self.tr("Add New " + option)) 
        else:
            #Check that we are not trying to delete the DM!
            if not (self.statementType == "voices" and self.itemAt(position).text() == "DM"):
                delStatement = menu.addAction(self.tr("Delete " + option))
        action = menu.exec_(self.viewport().mapToGlobal(position))
        if action == addStatement:
            # print ("Adding Statement")
            self.addStatement()
        elif action == delStatement:
            # print("Deleting Statement")
            self.deleteStatement(position)


    def addItems(self):
        # print ("Common Statements " + str(self.statementList.getStatements()))
        for state in self.statementList.getStatements(): 
            # print ("text" + str(state.getLWItem().text()))
            self.addItem(state.getLWItem())

    def populate(self):
        self.clear()
        self.statementList.populate()
        self.addItems()

    def addStatement(self):
        self.statementList.add() #Add a new Item to the statementList
        DMInfo.setCategoryDict(self.statementType, self.statementList)
        self.populate()

    def deleteStatement(self, position):
        delItem = self.itemAt(position)
        rowIndex = self.row(delItem)
        reply = QtGui.QMessageBox.question(self, 'Confirmation',
                    "Are you sure to delete the statement " "\"" + delItem.text() + "\"?", QtGui.QMessageBox.Yes | 
                    QtGui.QMessageBox.No, QtGui.QMessageBox.Yes)
        if reply == QtGui.QMessageBox.Yes:
            self.statementList.remove(rowIndex)
            DMInfo.setCategoryDict(self.statementType, self.statementList)
            self.populate()

    def editStatement(self):
        newText = self.currentItem().text()  #Grab the text from the ListWidget that has just had the text edited
        newStatementList = self.statementList.getStatements()
        # print("New Statement List : " + str(newStatementList) )
        newStatementList[self.currentRow()].setStatementText(newText)
        self.statementList.setStatements(newStatementList)
        DMInfo.setCategoryDict(self.statementType, self.statementList)
        self.populate()

    def reOrderStatementLists(self):
        newStatementList = []

        lWItems = []
        for index in xrange(self.count()):
             lWItems.append(self.item(index))
        for lw in lWItems:
            for state in self.statementList.getStatements():
                if lw is state.getLWItem():
                    newStatementList.append(state)
        self.statementList.setStatements(newStatementList)
        DMInfo.setCategoryDict(self.statementType, self.statementList)
        self.populate()


    def dropEvent(self, event):
        super(StatementsQLW,self).dropEvent(event)
        #When the drop has finished then we need to look through the new ListWidgetItems and aligh out List
        self.reOrderStatementLists()




class TabDialog(QtGui.QDialog):
    def __init__(self, fileName, parent=None):
        super(TabDialog, self).__init__(parent)

        tabLayout = QtGui.QVBoxLayout()
        self.tabWidget = QtGui.QTabWidget()
        self.tabWidget.addTab(CommonStatementsTab(), "Common")
        self.tabWidget.addTab(RelativeStatementsTab(), "Relative")
        self.tabWidget.addTab(QuestionsTab(), "Questions")
        self.tabWidget.addTab(QuestSpecificTab(), "Quest Specific")

        tabLayout.addWidget(self.tabWidget)


        userMessageLayout = QtGui.QVBoxLayout()
        userColumnWidth = 150
        userTabWidth = 500
        
        #Setup regarding List - This is going to dictate who the message is about
        regardLabel = QtGui.QLabel("REGARDING:")
        regardingListLW =  StatementsQLW(DMInfo, "regardings")
        regardingListLW.setMaximumWidth(userColumnWidth)

        #set up Message From List
        voiceListLW =  StatementsQLW(DMInfo, "voices")
        voiceListLW.setMaximumWidth(userColumnWidth)
        voices =[]

        #Grab all the voices
        voiceLabel = QtGui.QLabel("VOICE ORIGIN:")
        voiceListLW.setCurrentRow(0)
        # voiceListLW.setMaximumHeight(19*len(DMInfo.getCategoryDict("voices").getStatements()))
        voiceListLW.setMaximumHeight(19*4)


        #Setup player List
        playerLabel = QtGui.QLabel("SEND TO PLAYER:")
        playerListLW =  QtGui.QListWidget()
        playerListLW.setMaximumWidth(userColumnWidth)
        players = []

        #Grab all the Players
        playerList = DMInfo.getPlayers()
        for text in playerList:
            players.append(text["character"] + " (" + text['name'] + ")")

        playerListLW.insertItems(0, players)
        playerListLW.setMaximumHeight(18*len(players))
        playerListLW.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)

        def findActiveStatement():
        	"""This function returns the listwidget and the selected row in a dictionary"""
        	#Find the list Widget in the Current Tab
        	activeList = self.tabWidget.currentWidget().layout().itemAt(0).widget()
        	# print activeList
        	# print type(activeList)
        	if len(activeList.selectedIndexes()) != 0:
        		# print activeList.selectedIndexes()[0].row()
        		return {'activeListWidget':activeList, "activeStatement" : activeList.selectedIndexes()[0].row()}
        	else:
        		return {'activeListWidget':None, "activeStatement" : None}

        def findActiveRegard():
        	if len(regardingListLW.selectedIndexes()) != 0:
        		# print "Active Regard: " + regardingListLW.item(regardingListLW.selectedIndexes()[0].row()).text()
        		return regardingListLW.item(regardingListLW.selectedIndexes()[0].row()).text()
        	else:
        		return None

        def findActiveVoice():
        	# print "Active Voice: " + str(voiceListLW.selectedIndexes()[0].row())
        	return voiceListLW.selectedIndexes()[0].row()

        def findActivePlayers():
        	activePlayerList = []
        	for index in playerListLW.selectedIndexes():
        		activePlayerList.append(index.row())
        	# print activePlayerList
        	return activePlayerList

        def processMessage():
        	activeStatementDict = findActiveStatement()
        	if activeStatementDict["activeListWidget"]:
        		statement = activeStatementDict["activeListWidget"].item(activeStatementDict["activeStatement"]).text()
        		#Now check if the statement splits - if it does then it requires a regard 
        		splitStatement = statement.split("####")
        		if len(splitStatement) > 1:
        			#The statement has split so collect the regard
        			activeRegard = findActiveRegard()
        			if activeRegard:
        				#Awkard check code to see where we insert the name. If both sections of the split string has characters we insert in the middle. If not we insert on the empty string
        				insertTarget = 2 #this represents the name having to be inserted into the middle
        				for i, splitPhrase in enumerate(splitStatement):
        					if len(splitPhrase) == 0: insertTarget = i
        				#Now we hardcode build the string - messy!
        				if insertTarget == 0:
        					statement = "*" + activeRegard + "*" + splitStatement[1]
        				elif insertTarget == 1:
        					statement = splitStatement[0] + "*" + activeRegard + "*"
        				elif insertTarget == 2:
        					statement = splitStatement[0] + "*" + activeRegard + "*" + splitStatement[1]
        			else: return None
        		return statement
        	else: 
        		return None

        def sendMessage():
        	finalVoice = findActiveVoice()
        	# print "Voice: " + str(finalVoice)
        	finalPlayers = findActivePlayers()
        	# print "Players: " + str(findActivePlayers)
        	finalStatement = processMessage()
        	# print "Statement: " + str(findActiveStatement)
        	# print "My final Statement is: " + str(finalStatement)
        	if (len(finalPlayers) != 0) and finalStatement: #If all if these conditions are met then we should be able to send the message
        		voicename = voiceListLW.getStatementList().getStatements()[finalVoice].get()["name"]  #Grabbing the RawJson
        		asUser = int(voiceListLW.getStatementList().getStatements()[finalVoice].get()["asUser"]) #Grabbing the Raw Json
        		print "Message: " + finalStatement
        		for playerNum in finalPlayers:
        			playerID = playerList[playerNum]["slackID"]
        			slack_client.api_call("chat.postMessage", channel=playerID, text=finalStatement, as_user=asUser, username=voicename )    #Using text to add an emoji
        			print "SENDING TO: " + playerList[playerNum]["character"]
        	else:
        		print "Message failed to SEND"


        sendButton = QtGui.QPushButton("SEND SLACK MESSAGE")
        sendButton.setMinimumHeight(50)
        sendButton.setMaximumWidth(userColumnWidth)
        sendButton.clicked.connect(sendMessage)

        userMessageLayout.addWidget(regardLabel)
        userMessageLayout.addWidget(regardingListLW)
        userMessageLayout.addWidget(voiceLabel)
        userMessageLayout.addWidget(voiceListLW)
        userMessageLayout.addWidget(playerLabel)
        userMessageLayout.addWidget(playerListLW)
        userMessageLayout.addWidget(sendButton)

        mainLayout = QtGui.QHBoxLayout()
        mainLayout.addLayout(tabLayout)
        mainLayout.addLayout(userMessageLayout)

        # mainLayout.addWidget(tabWidget)
        # mainLayout.addWidget(buttonBox)
        self.setLayout(mainLayout)

        self.setWindowTitle("Dungeon Master - Fast Messenger")





class CommonStatementsTab(QtGui.QWidget):
    def __init__(self, parent=None):
        super(CommonStatementsTab, self).__init__(parent)
        statementsListBox = StatementsQLW(DMInfo, "CommonStatements")
        statementsListBox.setMinimumWidth(tabColumnWidth)
        layout = QtGui.QVBoxLayout()
        layout.addWidget(statementsListBox)
        self.setLayout(layout)


class RelativeStatementsTab(QtGui.QWidget):
    def __init__(self, parent=None):
        super(RelativeStatementsTab, self).__init__(parent)
        statementsListBox = StatementsQLW(DMInfo, "RelativeStatements")
        statementsListBox.setMinimumWidth(tabColumnWidth)
        layout = QtGui.QVBoxLayout()
        layout.addWidget(statementsListBox)
        self.setLayout(layout)

class QuestionsTab(QtGui.QWidget):
    def __init__(self, parent=None):
        super(QuestionsTab, self).__init__(parent)
        statementsListBox = StatementsQLW(DMInfo, "Questions")
        statementsListBox.setMinimumWidth(tabColumnWidth)
        layout = QtGui.QVBoxLayout()
        layout.addWidget(statementsListBox)
        self.setLayout(layout)


class QuestSpecificTab(QtGui.QWidget):
    def __init__(self, parent=None):
        super(QuestSpecificTab, self).__init__(parent)
        statementsListBox = StatementsQLW(DMInfo, "QuestStatements")
        statementsListBox.setMinimumWidth(tabColumnWidth)
        layout = QtGui.QVBoxLayout()
        layout.addWidget(statementsListBox)
        self.setLayout(layout)



if __name__ == '__main__':
	app = QtGui.QApplication(sys.argv)
	# setup stylesheet
	app.setStyleSheet(qdarkstyle.load_stylesheet())

	if len(sys.argv) >= 2:
	    fileName = sys.argv[1]
	else:
	    fileName = "."

	tabdialog = TabDialog(fileName)
	sys.exit(tabdialog.exec_())



#####################
#  List Widget Items .... self.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
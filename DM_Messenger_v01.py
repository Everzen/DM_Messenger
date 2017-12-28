from PySide import QtCore, QtGui
import sys
import qdarkstyle
import json
from slackclient import SlackClient



#Tempory development token to talk to SVFX-DND-ADVENTURE.slack.com - This validates user DM sending direct messages too! 

jsonFile = 'resources\MessengerData_SVFX.json'
# jsonFile = 'resources\MessengerData_DnKnee.json'
# jsonFile = 'resources\MessengerData_Illumria.json'

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
slackdevToken = DMInfo["security"]
slack_client = SlackClient(slackdevToken["DMToken"])


# print(str(DMInfo))

# print (" ----------------------------------------")

# DMInfo["voices"].append({"name" : "badger", "asUser" : 0})

# print(str(DMInfo))

def saveJson():
    with open(jsonFile, 'w') as json_file:
        json.dump(DMInfo, json_file)

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
        regardingListLW =  QtGui.QListWidget()
        regardingListLW.setMaximumWidth(userColumnWidth)
        regardingList = DMInfo["regardings"]

        regardingListLW.insertItems(0, regardingList)

        #set up Message From List
        voiceListLW =  QtGui.QListWidget()
        voiceListLW.setMaximumWidth(userColumnWidth)
        voices =[]

        #Grab all the voices
        voiceLabel = QtGui.QLabel("VOICE ORIGIN:")
        voiceList = DMInfo["voices"]
        for text in voiceList:
            voices.append(text["name"])

        voiceListLW.insertItems(0, voices)  
        voiceListLW.setCurrentRow(0)
        voiceListLW.setMaximumHeight(19*len(voices))

        #Setup player List
        playerLabel = QtGui.QLabel("SEND TO PLAYER:")
        playerListLW =  QtGui.QListWidget()
        playerListLW.setMaximumWidth(userColumnWidth)
        players = []

        #Grab all the Players
        playerList = DMInfo["players"]
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
        		voicename = voiceList[finalVoice]["name"]
        		asUser = int(voiceList[finalVoice]["asUser"])
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



class statementsQLW(QtGui.QListWidget):
    def __init__(self, statementType, parent=None):
        super(statementsQLW, self).__init__(parent)
        self.statementType = statementType
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu) #context menu for user data
        self.customContextMenuRequested.connect(self.userMenu)
        self.itemChanged.connect(self.editStatement)  #This is called when the enter key is pressed on the changing of the edited text
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDragDropMode(QtGui.QAbstractItemView.InternalMove)


    def userMenu(self, position):
        menu = QtGui.QMenu()
        addStatement = "Nothing"
        editStatement = "Nothing"
        delStatement = "Nothing"
        if not (self.itemAt(position)): #Test right Click Position - have we hit an item
            addStatement = menu.addAction(self.tr("Add New Statement"))
        else: 
            # editStatement = menu.addAction(self.tr("Edit Statement"))
            delStatement = menu.addAction(self.tr("Delete Statement"))
        action = menu.exec_(self.viewport().mapToGlobal(position))
        if action == addStatement:
            # print ("Adding Statement")
            self.addStatement()
        elif action == delStatement:
            # print("Deleting Statement")
            self.deleteStatement(position)


    def addItems(self, statementList):
        LItems = []
        for text in statementList:
            newListItem = QtGui.QListWidgetItem((text["statement"]))
            newListItem.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsDragEnabled | QtCore.Qt.ItemIsDropEnabled)
            self.addItem(newListItem)

    def populate(self):
        self.clear()
        self.addItems(DMInfo[self.statementType])

    def addStatement(self):
        DMInfo[self.statementType].append({"visible":1, "statement": "Edit this new Statement"})
        saveJson() #Save the new Json File
        self.populate()

    def deleteStatement(self, position):
        delItem = self.itemAt(position)
        rowIndex = self.row(delItem)
        reply = QtGui.QMessageBox.question(self, 'Confirmation',
                    "Are you sure to delete the statement " "\"" + delItem.text() + "\"?", QtGui.QMessageBox.Yes | 
                    QtGui.QMessageBox.No, QtGui.QMessageBox.Yes)
        if reply == QtGui.QMessageBox.Yes:
            del(DMInfo[self.statementType][rowIndex])
            saveJson() #Save the new Json File
            self.populate()

    def editStatement(self):
        newText = self.currentItem().text()  #Grab the text from the ListWidget that has just had the text edited
        DMInfo[self.statementType][self.currentRow()]["statement"] = newText  #Change the associated part of the json
        saveJson()


class CommonStatementsTab(QtGui.QWidget):
    def __init__(self, parent=None):
        super(CommonStatementsTab, self).__init__(parent)

        statementsListBox = statementsQLW("CommonStatements")
        statementsListBox.setMinimumWidth(tabColumnWidth)
        statements = []

        #Grab all the common Questions
        commonStatements = DMInfo["CommonStatements"]
        statementsListBox.addItems(commonStatements)
        layout = QtGui.QVBoxLayout()
        layout.addWidget(statementsListBox)
        self.setLayout(layout)


class RelativeStatementsTab(QtGui.QWidget):
    def __init__(self, parent=None):
        super(RelativeStatementsTab, self).__init__(parent)
        statementsListBox = QtGui.QListWidget()
        statementsListBox.setMinimumWidth(tabColumnWidth)
        statements = []

        #Grab all the common Questions
        commonStatements = DMInfo["RelativeStatements"]
        for text in commonStatements:
            statements.append(text["statement"])

        statementsListBox.insertItems(0, statements)
        layout = QtGui.QVBoxLayout()
        layout.addWidget(statementsListBox)
        self.setLayout(layout)

class QuestionsTab(QtGui.QWidget):
    def __init__(self, parent=None):
        super(QuestionsTab, self).__init__(parent)

        statementsListBox = QtGui.QListWidget()
        statementsListBox.setMinimumWidth(tabColumnWidth)
        statements = []

        #Grab all the common Questions
        commonStatements = DMInfo["Questions"]
        for text in commonStatements:
            statements.append(text["statement"])

        statementsListBox.insertItems(0, statements)
        layout = QtGui.QVBoxLayout()
        layout.addWidget(statementsListBox)
        self.setLayout(layout)


class QuestSpecificTab(QtGui.QWidget):
    def __init__(self, parent=None):
        super(QuestSpecificTab, self).__init__(parent)

        statementsListBox = QtGui.QListWidget()
        statementsListBox.setMinimumWidth(tabColumnWidth)
        statements = []

        #Grab all the common Questions
        commonStatements = DMInfo["QuestStatements"]
        for text in commonStatements:
            statements.append(text["statement"])

        statementsListBox.insertItems(0, statements)
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
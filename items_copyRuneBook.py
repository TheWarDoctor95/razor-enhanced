# If copying a locked down book, DO THIS BEFORE STARTING
#   Mark a rune for a location that you can reach the runebook being copied from AND
#   where you are close enough to recall off the book
#
#   Put this rune into a book for safe keeping (runes aren't blessed, runebooks are)
#   Set the rune as the default location for the book 
#   Select the correct book when the target comes up for 'Select item to recall off of to return to runebook being copied' 

import re
from Scripts import config
from Scripts.glossary.colors import colors
from Scripts.utilities.items import FindNumberOfItems

def PromptRunebook( promptString ):
    runebookSerial = Target.PromptTarget( promptString )
    runebook = Items.FindBySerial( runebookSerial )

    if runebook == None or runebook.ItemID != 0x22C5:
        Player.HeadMessage( colors[ 'red' ], 'That is not a runebook!' )
        return None
    else:
        return runebook

    
def GetNamesOfRunesInBook( runebook ):
    Items.UseItem( runebook )
    
    # Pause here since the next part goes pretty quick
    Misc.Pause( config.dragDelayMilliseconds )
    
    Gumps.WaitForGump( 1431013363, 5000 )
    if Gumps.CurrentGump() != 1431013363:
        Player.HeadMessage( colors[ 'red' ], 'Too far from runebook to copy' )
    
    runeNames = []
    lineList = Gumps.LastGumpGetLineList()
    
    # Remove the default 3 lines from the top of the list
    lineList = lineList[ 3 : ]
        
    # Remove the items before the names of the runes
    endIndexOfDropAndDefault = 0
    for i in range( 0, len( lineList ) ):
        if lineList[ i ] == 'Set default' or lineList[ i ] == 'Drop rune':
            endIndexOfDropAndDefault += 1
        else:
            break
    
    # Add two for the charge count and max charge numbers
    endIndexOfDropAndDefault += 2
    runeNames = lineList[ endIndexOfDropAndDefault : ( endIndexOfDropAndDefault + 16 ) ]
    runeNames = [ name for name in runeNames if name != 'Empty' ]
    
    return runeNames


def GetNumberOfRunesInBook( runebook ):
    return len( GetNamesOfRunesInBook( runebook ) )
    
        
def CopyRunebookName():
    global runebookToCopy
    global runebookToPlaceIn
    
    Journal.Clear()
    if Gumps.CurrentGump() == 1431013363:
        Gumps.WaitForGump( 1431013363, 1000 )
        Gumps.SendAction( 1431013363, 0 )
    
    Items.SingleClick( runebookToCopy.Serial )
    Misc.Pause( config.journalEntryDelayMilliseconds )
    runebookName = None
    for line in Journal.GetTextByType( 'Label' ):
        if '[' in line:
            bracketIndex = line.find( '[' )
            runebookName = line[ 0 : ( bracketIndex - 1 ) ]
                
    if runebookName != None and runebookName != '':
        Items.UseItem( runebookToPlaceIn )
        Gumps.WaitForGump( 1431013363, 10000 )
        Gumps.SendAction( 1431013363, 1 )
        Misc.WaitForPrompt( 1000 )
        Misc.ResponsePrompt( runebookName )
        Gumps.WaitForGump( 1431013363, 1000 )
        Gumps.SendAction( 1431013363, 0 )
        

def CopyRunebook():
    global runebookToCopy
    global runebookToPlaceIn
    
    runebookToCopy = PromptRunebook( 'Select the runebook to copy from' )
    if runebookToCopy == None:
        return
    
    runebookToPlaceIn = PromptRunebook( 'Select the runebook to copy to' )
    if runebookToPlaceIn == None:
        return
    
    # Test if the runebook is locked down or not 
    Journal.Clear()
    runebookMoveable = True
    if runebookToCopy.RootContainer != Player.Serial:
        Items.Move( runebookToCopy, Player.Backpack, 0 )
        Misc.Pause( config.dragDelayMilliseconds + 100 ) # plus 100 to be extra safe
        
        runebookToCopy = Items.FindBySerial( runebookToCopySerial )
        
        if runebookToCopy.RootContainer != Player.Serial:
            runebookMoveable = False
            Target.PromptTarget( 'Select item to recall off of to return to runebook being copied' )

    numberOfRunesInOldBook = GetNumberOfRunesInBook( runebookToCopy )
    numberOfRunesInNewBook = GetNumberOfRunesInBook( runebookToPlaceIn )
    runeNames = GetNamesOfRunesInBook( runebookToCopy )
    
    Misc.SendMessage( '# of runes to copy: %i' % numberOfRunesInOldBook )
    Misc.SendMessage( '# of runes already copied: %i' % numberOfRunesInNewBook )
    numberOfRunesToBeMarked = numberOfRunesInOldBook - numberOfRunesInNewBook

    # Make sure we have enough runes to be marked
    emptyRuneBagSerial = Target.PromptTarget( 'Select bag with empty runes' )
    emptyRuneBag = Items.FindBySerial( emptyRuneBagSerial )
    if emptyRuneBag == None or not emptyRuneBag.IsContainer:
        Player.HeadMessage( colors[ 'red' ], 'Invalid item selection!' )
        return
        
    numberOfEmptyRunes = 0
    for item in emptyRuneBag.Contains:
        if item.ItemID == 0x1F14:
            numberOfEmptyRunes += 1
    
    if numberOfRunesToBeMarked > numberOfEmptyRunes:
        Player.HeadMessage( colors[ 'red' ], 'You don\'t have enough empty runes to copy this book! You need %i more runes' % ( numberOfRunesToBeMarked - numberOfEmptyRunes ) )
        return
    
    # Copy the runebook
    for i in range( numberOfRunesInNewBook, numberOfRunesInOldBook ):
        Items.UseItem( runebookToCopy )
        Misc.Pause( config.dragDelayMilliseconds )
        Gumps.WaitForGump( 1431013363, 5000 )
        
        if i == 0:
            Gumps.SendAction( 1431013363, 5 )
        else:
            Gumps.SendAction( 1431013363, ( 5 + ( i * 6 ) ) )

        Timer.Create( 'spellCooldown', 2500 )
        Misc.Pause( 100 )
        playerPosition = Player.Position
        
        runeToMark = Items.FindByID( 0x1F14, -1, emptyRuneBag.Serial )
        
        while Timer.Check( 'spellCooldown' ):
            Misc.Pause( 50 )

        Spells.CastMagery( 'Mark' )
        Target.WaitForTarget( 2000, True )
        Target.TargetExecute( runeToMark )
        
        Timer.Create( 'spellCooldown', 1800 )
        
        Items.UseItem( runeToMark )

        Misc.WaitForPrompt( 1000 )
        Misc.ResponsePrompt( runeNames[ i ] )
        Misc.Pause( config.dragDelayMilliseconds )
        
        Items.Move( runeToMark, runebookToPlaceIn, 0 )
        Misc.Pause( config.dragDelayMilliseconds )
        
        if runebookMoveable:
            if Player.Mana < 41:
                Player.UseSkill( 'Meditation' )
                while Player.Mana < ( Player.ManaMax - 3 ):
                    Misc.Pause( 50 )
            
            while Timer.Check( 'spellCooldown' ):
                Misc.Pause( 50 )
        else:
            while Timer.Check( 'spellCooldown' ):
                Misc.Pause( 50 )

            if Player.Mana < 90:
                Player.UseSkill( 'Meditation' )
                while Player.Mana < 90:
                    if not Player.BuffsExist( 'Meditation' ):
                        Player.UseSkill( 'Meditation' )
                    Misc.Pause( 50 )
                
    Player.HeadMessage( colors[ 'green' ], 'Done copying runebook!' )

CopyRunebook()

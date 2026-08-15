from watchdog.events import FileSystemEventHandler
import os
from pathlib import Path
import pyautogui
import re

class DirectoryWatcherHandler(FileSystemEventHandler):

    def on_created(self, event):
        if not event.is_directory:
            self.triggerAction(event.src_path)

    def triggerAction(self, filePath):
        Directory.processSingleMissingGroup(filePath)

class Directory:

    def InitVar():
        Directory.folder = Path(__file__).parent
        Directory.subdirectory = next((sub for sub in Directory.folder.iterdir() if sub.is_dir() and "imgs" in str(sub)), None)

    def getLatestGroup() -> list[str]:
        filePath = os.path.join(Directory.folder, "translationgroups.txt")

        if not os.path.exists(filePath):
            raise FileNotFoundError(f"File not found: {filePath}")

        with open(filePath, 'r', encoding='utf-8') as file:
            lines = file.read().splitlines()

        headerIndices = [i for i, line in enumerate(lines) if line.strip().startswith("#")]

        SECTION_INDEX = 2

        if len(headerIndices) <= SECTION_INDEX:
            raise IndexError("La section n'existe pas dans le fichier translationgroups.txt")

        targetHeaderIndex = headerIndices[SECTION_INDEX]
        
        nextHeaderIndex = len(lines)
        for headerIndex in headerIndices:

            if headerIndex > targetHeaderIndex:
                nextHeaderIndex = headerIndex
                break

        sectionGroups = []
        for line in lines[targetHeaderIndex + 1 : nextHeaderIndex]:

            if line.strip() and not line.strip().startswith("#"):
                items = [item.strip() for item in line.split(",") if item.strip()]
                sectionGroups.extend(items)

        if not sectionGroups:
            raise ValueError("La section est vide")

        return sectionGroups


    def processSingleMissingGroup(directoryPath: Path):
        directoryPath = Path(directoryPath)
        
        sectionGroups = Directory.getLatestGroup()

        existingFilesStr = " ".join(os.listdir(directoryPath))
        
        missingGroup = None
        for group in sectionGroups:

            if f"_{group}" not in existingFilesStr:
                missingGroup = group
                break

        if missingGroup:
            renameChapterButtons(directoryPath, missingGroup)

    def updateTranslatorsGroupDoc(translatorGroup : str, index : int, addremove : bool):
        filePath = os.path.join(Directory.folder, "translationgroups.txt")
        maxColumns = 130

        with open(filePath, 'r', encoding='utf-8') as file:
            lines = file.read().splitlines()

        headerIndices = [
            i for i, line in enumerate(lines) 
            if line.strip().startswith("#")
        ]

        if index >= len(headerIndices):
            pyautogui.alert("L'index demandé dépasse les groupes configurés.")
            return

        targetHeaderIndex = headerIndices[index]
        nextHeaderIndex = len(lines)

        for headerIndex in headerIndices:

            if headerIndex > targetHeaderIndex:
                nextHeaderIndex = headerIndex
                break

        sectionLines = lines[targetHeaderIndex + 1 : nextHeaderIndex]
        existingGroups = []

        for line in sectionLines:

            if line.strip() and not line.strip().startswith("#"):
                items = [item.strip() for item in line.split(",") if item.strip()]
                existingGroups.extend(items)

        if addremove is True:
            existingGroups.append(translatorGroup)

        elif addremove is False:
            existingGroups.remove(translatorGroup)

        else:
            print("Il y a eu un problème dans le code")
            return

        existingGroups.sort(key=len)

        formattedLines = []
        currentLine = ""

        for group in existingGroups:

            if not currentLine:
                currentLine = group

            elif len(currentLine) + len(f",{group}") <= maxColumns:
                currentLine += f",{group}"

            else:
                formattedLines.append(currentLine)
                currentLine = group

        if currentLine:
            formattedLines.append(currentLine)
            formattedLines.append("")

        lines[targetHeaderIndex + 1 : nextHeaderIndex] = formattedLines

        with open(filePath, 'w', encoding='utf-8') as file:
            file.write("\n".join(lines) + "\n")

def getNextGroupFilename(prefix: str, translatorGroup: str, extension: str, existingFiles: list) -> str:
    """
    Generates filenames like:
      - NextChapterButton_GroupA.png (first occurrence)
      - NextChapterButton_GroupA2.png (second occurrence)
      - NextChapterButton_GroupA3.png (third occurrence)
    """
    pattern = re.compile(rf"^{re.escape(prefix)}_{re.escape(translatorGroup)}(\d*)")
    
    usedCounters = []
    for f in existingFiles:
        match = pattern.match(f)

        if match:
            counterStr = match.group(1)
            counter = int(counterStr) if counterStr else 1
            usedCounters.append(counter)

    if not usedCounters:
        return f"{prefix}_{translatorGroup}{extension}"
    
    nextCounter = max(usedCounters) + 1
    if nextCounter < 2:
        nextCounter = 2

    return f"{prefix}_{translatorGroup}{nextCounter}{extension}"


def renameChapterButtons(ultimatePath: Path, translatorGroup: str):
    if not translatorGroup:
        return
    
    pathObj = Path(ultimatePath)

    if not pathObj.exists():
        raise FileNotFoundError("Je n'ai pas l'air de trouver le fichier ou le dossier nécessaire")

    if pathObj.is_file():
        directory = pathObj.parent
        fileStem = pathObj.stem
        extension = pathObj.suffix

        if fileStem.startswith("NextChapterButton"):
            groupString = fileStem[len("NextChapterButton") : ]

        elif fileStem.startswith("PreviousChapterButton"):
            groupString = fileStem[len("PreviousChapterButton") : ]

        else:
            return

        rawParts = [group for group in groupString.split("_") if group]
        groups = set(rawParts)
        groups.add(translatorGroup)
        
        sortedSuffix = "_" + "_".join(sorted(list(groups)))

        originalNext = directory / f"NextChapterButton{groupString}{extension}"
        originalPrev = directory / f"PreviousChapterButton{groupString}{extension}"

        newNext = directory / f"NextChapterButton{sortedSuffix}{extension}"
        newPrev = directory / f"PreviousChapterButton{sortedSuffix}{extension}"

        if originalNext != newNext:
            originalNext.rename(newNext)
            
        if originalPrev != newPrev:
            originalPrev.rename(newPrev)

        return

    os.chdir(pathObj)
    files = os.listdir('.')

    unprocessedFiles = [
        file for file in files 
        if os.path.isfile(file) 
        and not file.startswith("NextChapterButton") 
        and not file.startswith("PreviousChapterButton")
    ]

    unprocessedFiles.sort(key=os.path.getmtime)

    if not unprocessedFiles:
        return

    for i in range(0, len(unprocessedFiles), 2):
        currentFiles = os.listdir('.')
        
        nextFile = unprocessedFiles[i]
        extension = os.path.splitext(nextFile)[1]
        newNameNextFile = getNextGroupFilename("NextChapterButton", translatorGroup, extension, currentFiles)
        os.rename(nextFile, newNameNextFile)

        if i + 1 < len(unprocessedFiles):
            currentFiles = os.listdir('.')
            previousFile = unprocessedFiles[i + 1]
            extension = os.path.splitext(previousFile)[1]
            newNamePreviousFile = getNextGroupFilename("PreviousChapterButton", translatorGroup, extension, currentFiles)
            os.rename(previousFile, newNamePreviousFile)
        else:
            pyautogui.alert("Image Next/Previous Button à rajouter")
            os._exit(0)

if __name__ == "__main__":
    print("Ce programme doit être lancé avec le fichier NavigationHtml.py")
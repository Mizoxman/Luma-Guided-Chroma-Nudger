# written by Mizox
# proof of concept chroma sharpening filter
# requires/written for python 3.10.11 and pillow 10.2.0
# written in Thonny

import PIL
from PIL import Image


def main():
    
    # take filenames and parameters
    print("Sequence mode:")
    print("1: single image")
    print("2: image sequence")
    ImgMode = input("Enter 1 or 2: ")
    SourceFileName = "0"
    SourceFilePrefix = "0"
    FileDigits = 0
    FileStart = 0
    FileEnd = 0
    SourceExt = "0"
    if (ImgMode == "1"):
        SourceFileName = input("Enter source file name: ")
    else:
        SourceFilePrefix = input("Enter sequence prefix: ")
        FileDigits = int(input("Enter number of digits for sequence number: "))
        FileStart = int(input("Enter starting value for sequence: "))
        FileEnd = int(input("Enter ending value for sequence: "))
        SourceExt = input("Enter sequence file extension: ")
    DestFileName = input("Enter output file name: ")
    #print("Number of taps:")
    #print("1: 5 taps")
    #print("2: 11 taps")
    #TapMode = input("Enter 1 or 2: ")
    TapMode = "1"
    print("Sharpen?")
    print("1: nudge only")
    print("2: nudge and sharpen")
    Sharpen = input("Enter 1 or 2: ")
    Sparse = input("Sampling Frequency (positive integer): ")
    Sparse = int(Sparse)
    LumaWeight = input("Enter Luma Weight: ")
    LumaWeight = int(LumaWeight)
    print("Threshold mode:")
    print("1: mild")
    print("2: medium")
    print("3: aggressive")
    ThreshMode = input("Enter 1, 2, or 3: ")
    MinThresh = input("Enter Minimum Threshold (noise floor): ")
    MaxThresh = input("Enter Maximum Threshold (always an edge): ")
    MinThresh = int(MinThresh)
    MaxThresh = int(MaxThresh)
    print("currently only supports BT601")
    #ColorSpace = input("Enter 1 or 2: ")
    
    if (TapMode == "1") and (Sharpen == "1"):
        LutName = "5-tap-nudge.txt"
    elif (TapMode == "1") and (Sharpen == "2"):
        LutName = "5-tap-sharp.txt"
    elif (TapMode == "2") and (Sharpen == "1"):
        LutName = "11-tap-nudge.txt"
    elif (TapMode == "2") and (Sharpen == "2"):
        LutName = "11-tap-sharp.txt"
    else:
        print("invalid parameters")
        exit()
    
    # load the correct LUT for nudging
    hand = open(LutName)
    count = 0
    for line in hand:
        line = line.rstrip()
        count = count + 1
        key = str(line[:5])
        val = str(line[6:])
        if (count == 1):
            NudgeLut = {key : val}
        else:
            NudgeLut[key] = val
    hand.close()
    
    looping = 0
    while (looping == 0):
        
        if (ImgMode == "1"):
            # open image
            try:
                SourceImage = Image.open(SourceFileName)
                looping = 1
            except:
                print("Invalid Image")
                exit()
        else:
            SourceFileName = (SourceFilePrefix + ('0' * (FileDigits - (len(str(FileStart))))) + str(FileStart) + SourceExt)
            SourceImage = Image.open(SourceFileName)
            if (FileStart >= FileEnd):
                looping = 1
        print(SourceImage.format, SourceImage.size, SourceImage.mode)
        SourceImage = SourceImage.convert("YCbCr")
        print("Converting to YCbCr")
        
        xsize, ysize = SourceImage.size
        OutImage = Image.new("YCbCr", (xsize, ysize))
        
        x = -1
        y = -1
        
        
        
        # 5 tap mode
        if (TapMode == "1"):
            while (y < (ysize-1)):
                y = y + 1
                x = -1
                while (x < (xsize-1)):
                    x = x + 1
                    Y, Cb, Cr = SourceImage.getpixel((x,y))
                    try:
                        Yn3, Cbn3, Crn3 = SourceImage.getpixel(((x-(3 * Sparse)),y))
                    except:
                        Yn3, Cbn3, Crn3 = 0, 128, 128
                    CbList = [Cbn3]
                    CrList = [Crn3]
                    try:
                        Yn2, Cbn2, Crn2 = SourceImage.getpixel(((x-(2 * Sparse)),y))
                    except:
                        Yn2, Cbn2, Crn2 = 0, 128, 128
                    YList = [Yn2]
                    CbList.append(Cbn2)
                    CrList.append(Crn2)
                    try:
                        Yn1, Cbn1, Crn1 = SourceImage.getpixel(((x-(1 * Sparse)),y))
                    except:
                        Yn1, Cbn1, Crn1 = 0, 128, 128
                    YList.append(Yn1)
                    CbList.append(Cbn1)
                    CrList.append(Crn1)
                    
                    YList.append(Y)
                    CbList.append(Cb)
                    CrList.append(Cr)
                    
                    try:
                        Yp1, Cbp1, Crp1 = SourceImage.getpixel(((x+(1 * Sparse)),y))
                    except:
                        Yp1, Cbp1, Crp1 = 0, 128, 128
                    YList.append(Yp1)
                    CbList.append(Cbp1)
                    CrList.append(Crp1)
                    try:
                        Yp2, Cbp2, Crp2 = SourceImage.getpixel(((x+(2 * Sparse)),y))
                    except:
                        Yp2, Cbp2, Crp2 = 0, 128, 128
                    YList.append(Yp2)
                    CbList.append(Cbp2)
                    CrList.append(Crp2)
                    try:
                        Yp3, Cbp3, Crp3 = SourceImage.getpixel(((x+(3 * Sparse)),y))
                    except:
                        Yp3, Cbp3, Crp3 = 0, 128, 128
                    CbList.append(Cbp3)
                    CrList.append(Crp3)
                    
                    Count = -1
                    while (Count < 4):
                        Count = Count + 1
                        if (Count == 0):
                            YList2 = [(abs(Y - (YList[Count])))]
                            CbList2 = [(abs(Cb - (CbList[(Count + 1)])))]
                            CrList2 = [(abs(Cr - (CrList[(Count + 1)])))]
                            CompList =[((YList2[Count]) * LumaWeight) + (CbList2[Count]) + (CrList2[Count])]
                        else:
                            YList2.append((abs(Y - (YList[Count]))))
                            CbList2.append((abs(Cb - (CbList[(Count + 1)]))))
                            CrList2.append((abs(Cr - (CrList[(Count + 1)]))))
                            CompList.append(((YList2[Count]) * LumaWeight) + (CbList2[Count]) + (CrList2[Count]))
                    
                    Thresh = max(CompList)
                    
                    if (ThreshMode == "1"):
                        Thresh = Thresh * 0.75
                    elif (ThreshMode == "2"):
                        Thresh = Thresh * 0.5
                    else:
                        Thresh = Thresh * 0.25
                    
                    if (Thresh > MaxThresh):
                        Thresh = MaxThresh
                    elif (Thresh < MinThresh):
                        Thresh = MinThresh
                    
                    Count = -1
                    
                    while (Count < 4):
                        Count = Count + 1
                        if ((CompList[Count]) < Thresh):
                            Pass = "1"
                        else:
                            Pass = "0"
                        if (Count == 0):
                            YList3 = Pass
                        else:
                            YList3 = YList3 + Pass
                    
                    
                    Nudging = NudgeLut.get(YList3)
                    
                    #if (x == 2) and (y == 91):
                        #print(YList)
                        #print(CbList)
                        #print(CrList)
                        #print(CompList)
                        #print(YList3)
                        #print(Nudging)
                    
                    Count = -1
                    
                    Cb = 0
                    Cr = 0
                    
                    while (Count < 6):
                        Count = Count + 1
                        if (Nudging[Count] == "-"):
                            Cb = Cb + 0
                            Cr = Cr + 0
                        elif (Nudging[Count] == "n"):
                            Cb = Cb - CbList[Count]
                            Cr = Cr - CrList[Count]
                        else:
                            shift = int(Nudging[Count])
                            Cb = Cb + ((CbList[Count]) << shift)
                            Cr = Cr + ((CrList[Count]) << shift)
                    
                    Cb = int(Cb / 2)
                    Cr = int(Cr / 2)
                    
                    OutImage.putpixel( (x, y), (Y, Cb, Cr) )
        
        OutImage = OutImage.convert("RGB")
        
        if (ImgMode == "1"):
            OutFileName = DestFileName + ".png"
            OutImage.save(OutFileName)
        else:
            OutFileName = (DestFileName + ('0' * (FileDigits - (len(str(FileStart))))) + str(FileStart) + ".png")
            OutImage.save(OutFileName)
            FileStart = FileStart + 1
        print("Exporting " + OutFileName)
        SourceImage.close()
        OutImage.close()
    
    
    
    return

main()
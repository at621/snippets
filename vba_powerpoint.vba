Sub CreatePPointSlides()
Dim PowPntApp As PowerPoint.Application
Dim PowPntPrsnt As PowerPoint.Presentation
Dim PowPntSlide As PowerPoint.Slide
Dim StrFile, strPath As String

' Create PowerPoint instance
Set PowPntApp = New PowerPoint.Application
PowPntApp.Visible = True
PowPntApp.Activate

Set PowPntPrsnt = PowPntApp.Presentations.Add

' Create first slide
Set PowPntSlide = PowPntPrsnt.Slides.Add(1, ppLayoutTitle)
PowPntSlide.Shapes(1).TextFrame.TextRange = "Univariate analysis results"
PowPntSlide.Shapes(2).TextFrame.TextRange = "Jim Beam"

' Create paths
strPath = "C:\Users\Watson\Pictures\vba\"
StrFile = Dir("C:\Users\Watson\Pictures\vba\*.png")

i = 1

Do While Len(StrFile) > 0
    ' Add slides
    Set PowPntSlide = PowPntPrsnt.Slides.Add(i + 1, ppLayoutTitle)
    
    ' Add picture
    PowPntSlide.Shapes.AddPicture strPath & StrFile, True, True, 100, 100, 70, 70
    
    ' Clean up
    i = i + 1
    StrFile = Dir
    
Loop


End Sub
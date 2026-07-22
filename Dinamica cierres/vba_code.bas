Attribute VB_Name = "Module1"
' Código VBA completo para exportación con doble clic

Sub Worksheet_BeforeDoubleClick(ByVal Target As Range, Cancel As Boolean)
    On Error GoTo ErrorHandler
    
    If Target.Value = "" Then Exit Sub
    If Target.Row < 9 Then Exit Sub
    
    If Not Target.Comment Is Nothing Then
        Dim commentText As String
        commentText = Target.Comment.Text
        
        If InStr(commentText, "Macro:") > 0 Then
            Cancel = True
            ProcessMacroComment commentText
        End If
    Else
        If Target.Font.Color = RGB(0, 102, 204) Or Target.Interior.Color = RGB(230, 243, 255) Then
            Cancel = True
            ProcessCellClick Target
        End If
    End If
    
    Exit Sub
    
ErrorHandler:
    MsgBox "Error en macro: " & Err.Description, vbExclamation
End Sub

Sub ProcessMacroComment(commentText As String)
    Dim parts() As String
    parts = Split(commentText, "|")
    
    If UBound(parts) < 1 Then Exit Sub
    
    Dim macroType As String
    macroType = Replace(parts(0), "Macro:", "")
    
    Select Case macroType
        Case "ExportTipoTrabajo"
            If UBound(parts) >= 1 Then
                RunPythonExport "tipo_trabajo", parts(1)
            End If
            
        Case "ExportTipoTrabajoFecha"
            If UBound(parts) >= 2 Then
                RunPythonExport "tipo_trabajo_fecha", parts(1), parts(2)
            End If
            
        Case "ExportAliado"
            If UBound(parts) >= 1 Then
                RunPythonExport "aliado", parts(1)
            End If
            
        Case "ExportAliadoFecha"
            If UBound(parts) >= 2 Then
                RunPythonExport "aliado_fecha", parts(1), parts(2)
            End If
    End Select
End Sub

Sub ProcessCellClick(Target As Range)
    Dim sheetName As String
    sheetName = ActiveSheet.Name
    
    If sheetName = "Visión Diaria" Then
        ProcessVisionDiariaClick Target
    ElseIf sheetName = "Resumen por Aliado" Then
        ProcessAliadoClick Target
    End If
End Sub

Sub ProcessVisionDiariaClick(Target As Range)
    If Target.Column = 1 And Target.Row >= 10 Then
        RunPythonExport "tipo_trabajo", Target.Value
    ElseIf Target.Column >= 4 And Target.Row >= 10 Then
        Dim trabajo As String
        Dim fecha As String
        trabajo = Cells(Target.Row, 1).Value
        fecha = Cells(9, Target.Column).Value
        RunPythonExport "tipo_trabajo_fecha", trabajo, fecha
    End If
End Sub

Sub ProcessAliadoClick(Target As Range)
    If Target.Column = 1 And Target.Row >= 5 Then
        RunPythonExport "aliado", Target.Value
    ElseIf Target.Column >= 2 And Target.Row >= 5 Then
        Dim aliado As String
        Dim fecha As String
        aliado = Cells(Target.Row, 1).Value
        fecha = Cells(4, Target.Column).Value
        RunPythonExport "aliado_fecha", aliado, fecha
    End If
End Sub

Sub RunPythonExport(tipo_filtro As String, valor_filtro As String, Optional fecha As String = "")
    On Error GoTo ErrorHandler
    
    Dim result As String
    
    If fecha = "" Then
        result = xlwings.RunPython("export_detalle('" & tipo_filtro & "', '" & valor_filtro & "')")
    Else
        result = xlwings.RunPython("export_detalle('" & tipo_filtro & "', '" & valor_filtro & "', '" & fecha & "')")
    End If
    
    If Left(result, 6) = "Error:" Then
        MsgBox result, vbExclamation
    Else
        MsgBox result, vbInformation
    End If
    
    Exit Sub
    
ErrorHandler:
    MsgBox "Error ejecutando Python: " & Err.Description, vbExclamation
End Sub
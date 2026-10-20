# Abre el informe en Word, actualiza el indice y los campos, lo guarda y exporta el PDF.
# Uso (desde la raiz del repo):
#   python docs/generar_informe.py
#   powershell -File docs/herramientas/actualizar-informe.ps1
param(
  [string]$Docx = (Join-Path $PSScriptRoot "..\Informe_Tecnico_Modulo_Desembolso.docx")
)
$ErrorActionPreference = "Stop"
$ruta = (Resolve-Path $Docx).Path
$pdf = [System.IO.Path]::ChangeExtension($ruta, ".pdf")

$word = New-Object -ComObject Word.Application
$word.Visible = $false
$word.DisplayAlerts = 0
try {
  $doc = $word.Documents.Open($ruta, $false, $false)
  foreach ($indice in $doc.TablesOfContents) { $indice.Update() }
  $doc.Fields.Update() | Out-Null
  $doc.Save()
  $doc.ExportAsFixedFormat($pdf, 17)
  $doc.Close([ref]0)
  Write-Host "Actualizado: $ruta"
  Write-Host "PDF:         $pdf"
} finally {
  $word.Quit()
  [System.Runtime.InteropServices.Marshal]::ReleaseComObject($word) | Out-Null
}

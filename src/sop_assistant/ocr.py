"""Windows OCR fallback without a local ML model or external API."""

import base64
import subprocess
import sys

import pymupdf

SCRIPT = r"""
$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = New-Object System.Text.UTF8Encoding
Add-Type -AssemblyName System.Runtime.WindowsRuntime
$null=[Windows.Storage.Streams.InMemoryRandomAccessStream,Windows.Storage.Streams,ContentType=WindowsRuntime]
$null=[Windows.Storage.Streams.DataWriter,Windows.Storage.Streams,ContentType=WindowsRuntime]
$null=[Windows.Graphics.Imaging.BitmapDecoder,Windows.Graphics.Imaging,ContentType=WindowsRuntime]
$null=[Windows.Media.Ocr.OcrEngine,Windows.Foundation,ContentType=WindowsRuntime]
function Await($op,$type) {
 $m=[System.WindowsRuntimeSystemExtensions].GetMethods() | Where-Object { $_.Name -eq 'AsTask' -and $_.IsGenericMethod -and $_.GetParameters().Count -eq 1 -and $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncOperation`1' } | Select-Object -First 1
 $t=$m.MakeGenericMethod($type).Invoke($null,@($op))
 $t.Wait()
 $t.Result
}

$stream=New-Object Windows.Storage.Streams.InMemoryRandomAccessStream
$writer=New-Object Windows.Storage.Streams.DataWriter($stream)
$writer.WriteBytes([Convert]::FromBase64String('IMAGE_DATA'))
$null=Await ($writer.StoreAsync()) ([uint32])
$stream.Seek(0)
$decoder=Await ([Windows.Graphics.Imaging.BitmapDecoder]::CreateAsync($stream)) ([Windows.Graphics.Imaging.BitmapDecoder])
$bitmap=Await ($decoder.GetSoftwareBitmapAsync()) ([Windows.Graphics.Imaging.SoftwareBitmap])
$engine=[Windows.Media.Ocr.OcrEngine]::TryCreateFromUserProfileLanguages()
if ($null -eq $engine) { throw 'No Windows OCR language available' }
$result=Await ($engine.RecognizeAsync($bitmap)) ([Windows.Media.Ocr.OcrResult])
$result.Lines | ForEach-Object { $_.Text }
"""


def windows_ocr(page) -> str:
    """Render in memory and recognize with the installed Windows language pack."""
    if sys.platform != "win32":
        raise ValueError("Scanned PDFs need Windows OCR on this version; see README.")
    image = page.get_pixmap(matrix=pymupdf.Matrix(2, 2)).tobytes("png")
    script = SCRIPT.replace("IMAGE_DATA", base64.b64encode(image).decode("ascii"))
    try:
        result = subprocess.run(
            ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", "-"],
            input=script,
            text=True,
            encoding="utf-8",
            capture_output=True,
            timeout=90,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        raise ValueError("Windows OCR could not start or timed out.") from None
    if result.returncode or result.stderr.strip():
        raise ValueError("Windows OCR failed; check that an OCR language pack is installed.")
    return result.stdout.strip()

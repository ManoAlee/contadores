# PowerShell GUI launcher for Contadores app
# Run with: powershell -ExecutionPolicy Bypass -File .\app\scripts\ps_gui_launcher.ps1

Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

# Verifica se a thread atual está em STA — necessário para Windows Forms
try {
    $apartment = [System.Threading.Thread]::CurrentThread.ApartmentState.ToString()
} catch {
    $apartment = 'Unknown'
}
if ($apartment -ne 'STA'){
    [System.Windows.Forms.MessageBox]::Show('PowerShell não está em modo STA. Reabra usando: powershell -STA -NoProfile -ExecutionPolicy Bypass -File "app\\scripts\\ps_gui_launcher.ps1"','Incompatibilidade de Thread', 'OK', 'Warning')
    exit 1
}

$form = New-Object System.Windows.Forms.Form
$form.Text = 'Contadores - Launcher (PowerShell GUI)'
$form.Size = New-Object System.Drawing.Size(880,640)
$form.StartPosition = 'CenterScreen'

# Labels and inputs
$lblPython = New-Object System.Windows.Forms.Label
$lblPython.Text = 'Python (venv) executable:'
$lblPython.Location = New-Object System.Drawing.Point(10,10)
$lblPython.Size = New-Object System.Drawing.Size(180,20)
$form.Controls.Add($lblPython)

$txtPython = New-Object System.Windows.Forms.TextBox
$txtPython.Location = New-Object System.Drawing.Point(200,10)
$txtPython.Size = New-Object System.Drawing.Size(520,20)
$defaultPy = Join-Path (Get-Location) '.venv\Scripts\python.exe'
$txtPython.Text = $defaultPy
$form.Controls.Add($txtPython)

$lblCLI = New-Object System.Windows.Forms.Label
$lblCLI.Text = 'CLI script:'
$lblCLI.Location = New-Object System.Drawing.Point(10,40)
$lblCLI.Size = New-Object System.Drawing.Size(180,20)
$form.Controls.Add($lblCLI)

$txtCLI = New-Object System.Windows.Forms.TextBox
$txtCLI.Location = New-Object System.Drawing.Point(200,40)
$txtCLI.Size = New-Object System.Drawing.Size(520,20)
$txtCLI.Text = Join-Path (Get-Location) 'app\scripts\cli_launcher.py'
$form.Controls.Add($txtCLI)

# Email file, IPs file, out dir, community
$lblEmail = New-Object System.Windows.Forms.Label
$lblEmail.Text = 'Email file:'
$lblEmail.Location = New-Object System.Drawing.Point(10,80)
$lblEmail.Size = New-Object System.Drawing.Size(180,20)
$form.Controls.Add($lblEmail)
$txtEmail = New-Object System.Windows.Forms.TextBox
$txtEmail.Location = New-Object System.Drawing.Point(200,80)
$txtEmail.Size = New-Object System.Drawing.Size(520,20)
$txtEmail.Text = Join-Path (Get-Location) 'app\data\incoming_email.txt'
$form.Controls.Add($txtEmail)

$lblIPs = New-Object System.Windows.Forms.Label
$lblIPs.Text = 'IPs file:'
$lblIPs.Location = New-Object System.Drawing.Point(10,110)
$lblIPs.Size = New-Object System.Drawing.Size(180,20)
$form.Controls.Add($lblIPs)
$txtIPs = New-Object System.Windows.Forms.TextBox
$txtIPs.Location = New-Object System.Drawing.Point(200,110)
$txtIPs.Size = New-Object System.Drawing.Size(520,20)
$txtIPs.Text = Join-Path (Get-Location) 'app\data\ips.txt'
$form.Controls.Add($txtIPs)

$lblOut = New-Object System.Windows.Forms.Label
$lblOut.Text = 'Output folder:'
$lblOut.Location = New-Object System.Drawing.Point(10,140)
$lblOut.Size = New-Object System.Drawing.Size(180,20)
$form.Controls.Add($lblOut)
$txtOut = New-Object System.Windows.Forms.TextBox
$txtOut.Location = New-Object System.Drawing.Point(200,140)
$txtOut.Size = New-Object System.Drawing.Size(520,20)
$txtOut.Text = Join-Path (Get-Location) 'app\data'
$form.Controls.Add($txtOut)

$lblComm = New-Object System.Windows.Forms.Label
$lblComm.Text = 'SNMP Community:'
$lblComm.Location = New-Object System.Drawing.Point(10,170)
$lblComm.Size = New-Object System.Drawing.Size(180,20)
$form.Controls.Add($lblComm)
$txtComm = New-Object System.Windows.Forms.TextBox
$txtComm.Location = New-Object System.Drawing.Point(200,170)
$txtComm.Size = New-Object System.Drawing.Size(120,20)
$txtComm.Text = 'public'
$form.Controls.Add($txtComm)

# Buttons
$btnRunSNMP = New-Object System.Windows.Forms.Button
$btnRunSNMP.Text = 'Executar SNMP'
$btnRunSNMP.Location = New-Object System.Drawing.Point(750,100)
$btnRunSNMP.Size = New-Object System.Drawing.Size(100,30)
$form.Controls.Add($btnRunSNMP)

$btnGenDraft = New-Object System.Windows.Forms.Button
$btnGenDraft.Text = 'Gerar Rascunho'
$btnGenDraft.Location = New-Object System.Drawing.Point(750,60)
$btnGenDraft.Size = New-Object System.Drawing.Size(100,30)
$form.Controls.Add($btnGenDraft)

$chkSend = New-Object System.Windows.Forms.CheckBox
$chkSend.Text = 'Enviar por SMTP (usar keyring se salvo)'
$chkSend.Location = New-Object System.Drawing.Point(200,200)
$chkSend.Size = New-Object System.Drawing.Size(300,20)
$form.Controls.Add($chkSend)

$btnSendDraft = New-Object System.Windows.Forms.Button
$btnSendDraft.Text = 'Gerar e Enviar'
$btnSendDraft.Location = New-Object System.Drawing.Point(750,20)
$btnSendDraft.Size = New-Object System.Drawing.Size(100,30)
$form.Controls.Add($btnSendDraft)

# Log box
$txtLog = New-Object System.Windows.Forms.TextBox
$txtLog.Location = New-Object System.Drawing.Point(10,240)
$txtLog.Size = New-Object System.Drawing.Size(840,360)
$txtLog.Multiline = $true
$txtLog.ScrollBars = 'Vertical'
$txtLog.ReadOnly = $true
$form.Controls.Add($txtLog)

function Append-Log([string]$s){
    $txtLog.AppendText((Get-Date).ToString('yyyy-MM-dd HH:mm:ss') + ' - ' + $s + "`r`n")
}

# Abre um diálogo modal para entrada de dados SMTP (retorna hashtable ou $null se cancelado)
function Show-SMTPDialog(){
    Add-Type -AssemblyName System.Windows.Forms
    $dlg = New-Object System.Windows.Forms.Form
    $dlg.Text = 'Configurar SMTP'
    $dlg.Size = New-Object System.Drawing.Size(420,260)
    $dlg.StartPosition = 'CenterParent'

    $lblS = New-Object System.Windows.Forms.Label
    $lblS.Text = 'SMTP server:'
    $lblS.Location = New-Object System.Drawing.Point(10,10)
    $lblS.Size = New-Object System.Drawing.Size(120,20)
    $dlg.Controls.Add($lblS)
    $txtS = New-Object System.Windows.Forms.TextBox
    $txtS.Location = New-Object System.Drawing.Point(140,10)
    $txtS.Size = New-Object System.Drawing.Size(250,20)
    $dlg.Controls.Add($txtS)

    $lblP = New-Object System.Windows.Forms.Label
    $lblP.Text = 'Porta:'
    $lblP.Location = New-Object System.Drawing.Point(10,40)
    $lblP.Size = New-Object System.Drawing.Size(120,20)
    $dlg.Controls.Add($lblP)
    $txtP = New-Object System.Windows.Forms.TextBox
    $txtP.Location = New-Object System.Drawing.Point(140,40)
    $txtP.Size = New-Object System.Drawing.Size(80,20)
    $txtP.Text = '465'
    $dlg.Controls.Add($txtP)

    $lblU = New-Object System.Windows.Forms.Label
    $lblU.Text = 'Usuário:'
    $lblU.Location = New-Object System.Drawing.Point(10,70)
    $lblU.Size = New-Object System.Drawing.Size(120,20)
    $dlg.Controls.Add($lblU)
    $txtU = New-Object System.Windows.Forms.TextBox
    $txtU.Location = New-Object System.Drawing.Point(140,70)
    $txtU.Size = New-Object System.Drawing.Size(250,20)
    $dlg.Controls.Add($txtU)

    $lblPw = New-Object System.Windows.Forms.Label
    $lblPw.Text = 'Senha:'
    $lblPw.Location = New-Object System.Drawing.Point(10,100)
    $lblPw.Size = New-Object System.Drawing.Size(120,20)
    $dlg.Controls.Add($lblPw)
    $txtPw = New-Object System.Windows.Forms.TextBox
    $txtPw.Location = New-Object System.Drawing.Point(140,100)
    $txtPw.Size = New-Object System.Drawing.Size(250,20)
    $txtPw.UseSystemPasswordChar = $true
    $dlg.Controls.Add($txtPw)

    $btnOk = New-Object System.Windows.Forms.Button
    $btnOk.Text = 'OK'
    $btnOk.Location = New-Object System.Drawing.Point(140,140)
    $btnOk.Size = New-Object System.Drawing.Size(100,30)
    $btnOk.Add_Click({ $dlg.Tag = 'ok'; $dlg.Close() })
    $dlg.Controls.Add($btnOk)

    $btnCancel = New-Object System.Windows.Forms.Button
    $btnCancel.Text = 'Cancelar'
    $btnCancel.Location = New-Object System.Drawing.Point(260,140)
    $btnCancel.Size = New-Object System.Drawing.Size(100,30)
    $btnCancel.Add_Click({ $dlg.Tag = 'cancel'; $dlg.Close() })
    $dlg.Controls.Add($btnCancel)

    $dlg.ShowDialog() | Out-Null
    if ($dlg.Tag -ne 'ok'){ return $null }
    return @{ server = $txtS.Text; port = $txtP.Text; user = $txtU.Text; pass = $txtPw.Text }
}

function Run-CLI([string[]]$args){
    $python = $txtPython.Text
    if (-not (Test-Path $python)){
        Append-Log "Python não encontrado: $python"
        return 1
    }
    $command = @($python) + $args
    Append-Log "Executando: $($command -join ' ' )"
    try{
        $procOutput = & $python @args 2>&1
        if ($procOutput){
            Append-Log ($procOutput -join "`r`n")
        } else {
            Append-Log 'Executado com saída vazia.'
        }
        return 0
    } catch {
        Append-Log "Erro executando comando: $_"
        return 1
    }
}

$btnRunSNMP.Add_Click({
    $ips = $txtIPs.Text
    $comm = $txtComm.Text
    $cli = $txtCLI.Text
    if (-not (Test-Path $cli)) { Append-Log "CLI não encontrado: $cli"; return }
    Run-CLI @($cli, 'snmp', '--ips', $ips, '--community', $comm, '--out', $txtOut.Text)
})

$btnGenDraft.Add_Click({
    $email = $txtEmail.Text
    $ips = $txtIPs.Text
    $out = $txtOut.Text
    $comm = $txtComm.Text
    $cli = $txtCLI.Text
    if (-not (Test-Path $cli)) { Append-Log "CLI não encontrado: $cli"; return }
    if (-not (Test-Path $email)) { Append-Log "Arquivo de e-mail não encontrado: $email"; return }
    Run-CLI @($cli, 'draft', '--email', $email, '--ips', $ips, '--out', $out, '--community', $comm)
})

$btnSendDraft.Add_Click({
    $email = $txtEmail.Text
    $ips = $txtIPs.Text
    $out = $txtOut.Text
    $comm = $txtComm.Text
    $cli = $txtCLI.Text
    if (-not (Test-Path $cli)) { Append-Log "CLI não encontrado: $cli"; return }
    if (-not (Test-Path $email)) { Append-Log "Arquivo de e-mail não encontrado: $email"; return }
    # solicitar SMTP info se marcado; abrir diálogo modal para entrada
    if ($chkSend.Checked){
        $smtp = Show-SMTPDialog
        if (-not $smtp){ Append-Log 'Envio cancelado pelo usuário.'; return }
        $args = @($cli, 'draft', '--email', $email, '--ips', $ips, '--out', $out, '--community', $comm, '--send')
        if ($smtp.server) { $args += @('--smtp-server', $smtp.server) }
        if ($smtp.port) { $args += @('--smtp-port', $smtp.port) }
        if ($smtp.user) { $args += @('--smtp-user', $smtp.user) }
        if ($smtp.pass) { $args += @('--smtp-pass', $smtp.pass) }
        Run-CLI $args
    } else {
        Append-Log 'Marque a caixa "Enviar por SMTP" para fornecer dados e enviar.'
    }
})

try {
    [System.Windows.Forms.Application]::EnableVisualStyles()
    [System.Windows.Forms.Application]::Run($form)
} catch {
    $msg = "Erro ao abrir GUI: $($_.Exception.Message)`n$($_.Exception.StackTrace)"
    try { [System.Windows.Forms.MessageBox]::Show($msg, 'Erro', 'OK', 'Error') } catch { Write-Error $msg }
} finally {
    Append-Log 'GUI finalizado.'
}

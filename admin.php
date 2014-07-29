
<head>
	<meta content='width=device-width, initial-scale=1' name='viewport'/>
	<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
</head>

<body bgcolor="#EBEBEB">

<?php
try
{
	$db = new PDO('sqlite:settings.db');
}
catch (Exception $e)
{
	die('Erreur : ' . $e->getMessage());
}

$reponse = $db->query('SELECT * FROM settings');
$raw_settings = $reponse->fetchAll();

foreach($raw_settings as $setting)
{
	$settings[$setting['id']] = $setting['value'];
}

?>



<form action="cible.php" method="post">
<p>
Music library location:</br>
    <input type="text" name="location" value="<?php echo $settings['location'] ?>"/>
</p>
<p>
    <input type="submit" value="Sauvegarder" />
</p>
</form>

<?php


$reponse->closeCursor();
?>

</body>


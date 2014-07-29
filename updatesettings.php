<head>
	<meta content='width=device-width, initial-scale=1' name='viewport'/>
	<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
</head>

<body bgcolor="#EBEBEB">

<?php

header( "refresh:1; url=admin.php" );

try
{
	$db = new PDO('sqlite:settings.db');
}
catch (Exception $e)
{
	die('Erreur : ' . $e->getMessage());
}

$req = $db->prepare('UPDATE settings SET value = :value WHERE id = :id');

$req->execute(array(
	'id' => 'location',
	'value' => $_POST['location'],
	));

$req->closeCursor();

?>

Setting saved

<?php
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

print_r($db->errorInfo());

$req->closeCursor();

echo $_POST['location'];

?>

<?php
header( "refresh:1; url=index.php" );
try
{
	$db = new PDO('sqlite:library.db');
}
catch (Exception $e)
{
	die('Erreur : ' . $e->getMessage());
}

$req = $db->prepare('UPDATE songs SET vote = vote+1 WHERE id = :song');

$req->execute(array(
	'song' => $_POST['song'],
	));

echo 'Vote effectué';

$req->closeCursor();

?>

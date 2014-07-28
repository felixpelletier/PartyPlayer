
<head>
	<meta content='width=device-width, initial-scale=1' name='viewport'/>
	<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
</head>

<body bgcolor="#EBEBEB">

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

</body>

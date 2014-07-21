
<?php
try
{
	$db = new PDO('sqlite:library.db');
}
catch (Exception $e)
{
	die('Erreur : ' . $e->getMessage());
}

$reponse = $db->query('SELECT playlist.title, songs.vote FROM playlist INNER JOIN songs ON playlist.info=songs.id WHERE songs.played = (SELECT MIN(played) FROM songs) ORDER BY songs.vote DESC LIMIT 10');
while ($song = $reponse->fetch())
{
	
	echo $song[0] . ' ' . $song[1] . '</br>';

}

$reponse->closeCursor();
?>



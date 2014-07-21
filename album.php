<?php
try
{
	$db = new PDO('sqlite:library.db');
}
catch (Exception $e)
{
	die('Erreur : ' . $e->getMessage());
}

$reponse = $db->query('SELECT title from playlist WHERE id =' . $_POST['album']);
$album = $reponse->fetch();

echo 'Album "' . $album['title'] . '":'; ?> </br><?php

$reponse = $db->query(sprintf(" SELECT node.title, node.info, (COUNT(parent.title) - (sub_tree.depth + 1)) AS depth2
				FROM playlist AS node, playlist AS parent,playlist AS sub_parent,
				(
				    SELECT node.id, (COUNT(parent.title) - 1) AS depth
				    FROM playlist AS node, playlist AS parent
				    WHERE node.lft BETWEEN parent.lft AND parent.rgt
				    AND node.id = '%s'
				    GROUP BY node.id
				    HAVING depth = 1
				    ORDER BY node.id
				)AS sub_tree
				WHERE node.lft BETWEEN parent.lft AND parent.rgt
				AND node.lft BETWEEN sub_parent.lft AND sub_parent.rgt
				AND sub_parent.id = sub_tree.id
				GROUP BY node.id
				HAVING depth2 = 1 AND (SELECT played FROM songs WHERE id = node.info) = (SELECT MIN(played) FROM songs)
				ORDER BY node.title", $_POST['album']));

while ($song = $reponse->fetch())
{
?>
	<form action="song.php" method="post">
	<p>
	    <input type="hidden" name="song" value="<?php echo $song['info'] ?>" />
	    <input type="submit" value="<?php echo $song['title'] ?>" />
	</p>
	</form>
	<?php 
}

$reponse->closeCursor();

include("menu.php");

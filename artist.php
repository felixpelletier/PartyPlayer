

<head>
	<meta content='width=device-width, initial-scale=1' name='viewport'/>
	<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
</head>

<body bgcolor="#EBEBEB">

<?php
try
{
	$db = new PDO('sqlite:library.db');
}
catch (Exception $e)
{
	die('Erreur : ' . $e->getMessage());
}

$reponse = $db->query('SELECT title from playlist WHERE id =' . $_POST['artist']);
$artiste = $reponse->fetch();

echo 'Albums de ' . $artiste['title'] . ':'; ?> </br><?php

$reponse = $db->query(sprintf(" SELECT node.title, node.id, (COUNT(parent.title) - (sub_tree.depth + 1)) AS depth2
				FROM playlist AS node, playlist AS parent,playlist AS sub_parent,
				(
				    SELECT node.id, (COUNT(parent.title) - 1) AS depth
				    FROM playlist AS node, playlist AS parent
				    WHERE node.lft BETWEEN parent.lft AND parent.rgt
				    AND node.id = '%s'
				    GROUP BY node.id
				    HAVING depth = 0
				    ORDER BY node.id
				)AS sub_tree
				WHERE node.lft BETWEEN parent.lft AND parent.rgt
				AND node.lft BETWEEN sub_parent.lft AND sub_parent.rgt
				AND sub_parent.id = sub_tree.id
				GROUP BY node.id
				HAVING depth2 = 1
				ORDER BY node.title", $_POST['artist']));

while ($album = $reponse->fetch())
{
?>
	<form action="album.php" method="post">
	<p>
	    <input type="hidden" name="album" value="<?php echo $album['id'] ?>" />
	    <input type="submit" value="<?php echo $album['title'] ?>" />
	</p>
	</form>
	<?php 
}

$reponse->closeCursor();

include("menu.php");

?>

</body>

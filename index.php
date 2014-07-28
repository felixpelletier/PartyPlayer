
<head>
	<meta content='width=device-width, initial-scale=1' name='viewport'/>
	<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
</head>

<body bgcolor="#EBEBEB">
Artistes: 

<?php
try
{
	$db = new PDO('sqlite:library.db');
}
catch (Exception $e)
{
	die('Erreur : ' . $e->getMessage());
}

$reponse = $db->query(' SELECT node.title, node.id, (COUNT(parent.title) - 1) AS depth
                	FROM playlist AS node, playlist AS parent
                	WHERE node.lft BETWEEN parent.lft AND parent.rgt
                	GROUP BY node.id
                	HAVING depth = 0
                	ORDER BY node.title');

while ($artist = $reponse->fetch())
{
?>
	<form action="artist.php" method="post">
	<p>
	    <input type="hidden" name="artist" value="<?php echo $artist['id'] ?>" />
	    <input type="submit" value="<?php echo $artist['title'] ?>" />
	</p>
	</form>
	<?php 
}

$reponse->closeCursor();
?>

<?php include("menu.php"); ?>

</body>

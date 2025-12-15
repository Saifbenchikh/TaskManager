@echo off
color 0B
echo ==========================================
echo      ENVOI DE MON CODE VERS GITHUB
echo ==========================================
echo.
echo Etape 1 : Preparation des fichiers...
git add .
echo.

echo Etape 2 : Validation
set /p Message="Ecris ce que tu as fait (ex: J'ai ajoute le bouton) : "
git commit -m "%Message%"
echo.

echo Etape 3 : Envoi vers le Cloud...
git push
echo.
echo ==========================================
echo C'est fini ! Ton code est en ligne.
echo ==========================================
pause
#!/bin/bash
case "$GIT_COMMIT" in
    e91560d*)
        echo "Correction frontend: URL WebSocket dynamique, recentLoans par role, retour creation conversation"
        ;;
    65f3953*)
        echo "feat: piste d'audit, historique des statuts, graphiques, presence chat et indicateur de frappe"
        ;;
    02b0fb2*)
        echo "fix: Swagger 0 erreurs - ajout swagger_fake_view et reponses extend_schema"
        ;;
    c954507*)
        echo "fix: page connexion - espaces en trop dans renderCharts causant crash Vue"
        ;;
    2f05802*)
        echo "feat: optimisations et corrections multiples"
        ;;
    *)
        cat
        ;;
esac

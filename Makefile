.PHONY: help install run stop update test logs clean reset

help:
	@echo "📈 CAC 40 Data Pipeline - Commandes disponibles:"
	@echo ""
	@echo "  make install    - Installation complète du projet"
	@echo "  make run        - Lancer l'application"
	@echo "  make stop       - Arrêter l'application"
	@echo "  make update     - Mettre à jour les données"
	@echo "  make test       - Tester l'API"
	@echo "  make logs       - Voir les logs"
	@echo "  make clean      - Arrêter et nettoyer"
	@echo "  make reset      - Réinitialisation complète"
	@echo ""

install:
	@chmod +x *.sh
	@./install.sh

run:
	@./run.sh

stop:
	@./stop.sh

update:
	@./update_data.sh

test:
	@python test_api.py

logs:
	@docker-compose logs -f

clean:
	@docker-compose down

reset:
	@docker-compose down -v
	@./install.sh

build:
	@docker-compose build

up:
	@docker-compose up -d

down:
	@docker-compose down

ps:
	@docker-compose ps

shell:
	@docker-compose exec app bash

db:
	@docker-compose exec postgres psql -U cac40_user -d cac40_db

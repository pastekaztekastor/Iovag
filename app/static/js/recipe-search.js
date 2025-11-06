/**
 * Composant de recherche de recettes avec autocomplete intelligent
 */

class RecipeSearch {
    constructor(inputId, hiddenInputId, options = {}) {
        this.input = document.getElementById(inputId);
        this.hiddenInput = document.getElementById(hiddenInputId);
        this.menuId = options.menuId || null;
        this.typeRepas = options.typeRepas || '';
        this.currentRecipeId = options.currentRecipeId || null;
        this.placeholder = options.placeholder || 'Rechercher une recette ou un ingrédient...';

        this.resultsContainer = null;
        this.selectedIndex = -1;
        this.results = [];
        this.debounceTimer = null;

        this.init();
    }

    init() {
        if (!this.input) return;

        this.input.placeholder = this.placeholder;
        this.input.autocomplete = 'off';

        // Créer le conteneur de résultats
        this.resultsContainer = document.createElement('div');
        this.resultsContainer.className = 'recipe-search-results';
        this.resultsContainer.style.display = 'none';
        this.input.parentNode.style.position = 'relative';
        this.input.parentNode.appendChild(this.resultsContainer);

        // Ajouter les événements
        this.input.addEventListener('input', () => this.handleInput());
        this.input.addEventListener('focus', () => this.handleFocus());
        this.input.addEventListener('keydown', (e) => this.handleKeydown(e));
        this.input.addEventListener('blur', () => this.handleBlur());

        // Charger la recette initiale si elle existe
        if (this.currentRecipeId) {
            this.loadInitialRecipe();
        }
    }

    handleInput() {
        clearTimeout(this.debounceTimer);
        const query = this.input.value.trim();

        // Vider le champ caché si on efface tout
        if (query.length === 0) {
            this.hiddenInput.value = '';
        }

        // Toujours rechercher, même avec un champ vide
        this.debounceTimer = setTimeout(() => {
            this.search(query);
        }, 300);
    }

    handleFocus() {
        // Toujours afficher les suggestions au focus (même champ vide)
        const query = this.input.value.trim();
        this.search(query);
    }

    handleKeydown(e) {
        if (this.results.length === 0) return;

        switch(e.key) {
            case 'ArrowDown':
                e.preventDefault();
                this.selectedIndex = Math.min(this.selectedIndex + 1, this.results.length - 1);
                this.updateSelection();
                break;
            case 'ArrowUp':
                e.preventDefault();
                this.selectedIndex = Math.max(this.selectedIndex - 1, -1);
                this.updateSelection();
                break;
            case 'Enter':
                e.preventDefault();
                if (this.selectedIndex >= 0) {
                    this.selectRecipe(this.results[this.selectedIndex]);
                }
                break;
            case 'Escape':
                this.hideResults();
                break;
        }
    }

    handleBlur() {
        // Délai pour permettre le clic sur un résultat
        setTimeout(() => this.hideResults(), 200);
    }

    async search(query) {
        try {
            const params = new URLSearchParams({
                q: query,
                type_repas: this.typeRepas
            });

            if (this.menuId) {
                params.append('menu_id', this.menuId);
            } else {
                // En mode création, récupérer les recettes déjà sélectionnées dans le formulaire
                const recettesSelectionnees = this.getRecettesSelectionnees();
                if (recettesSelectionnees.length > 0) {
                    params.append('recettes_menu', recettesSelectionnees.join(','));
                }
            }

            const response = await fetch(`/recettes/api/search?${params}`);
            const data = await response.json();

            this.results = data;
            this.displayResults();
        } catch (error) {
            console.error('Erreur lors de la recherche:', error);
        }
    }

    getRecettesSelectionnees() {
        // Récupérer tous les hidden inputs de recettes dans le formulaire
        const form = this.input.closest('form');
        if (!form) return [];

        const recetteIds = [];
        const hiddenInputs = form.querySelectorAll('input[type="hidden"][name^="jour_"]');

        hiddenInputs.forEach(input => {
            if (input.value && input.value.trim() !== '') {
                recetteIds.push(parseInt(input.value));
            }
        });

        return [...new Set(recetteIds)]; // Supprimer les doublons
    }

    displayResults() {
        if (this.results.length === 0) {
            this.resultsContainer.innerHTML = '<div class="recipe-search-no-result">Aucune recette trouvée</div>';
            this.resultsContainer.style.display = 'block';
            this.addActiveClass();
            return;
        }

        let html = '';
        this.results.forEach((recette, index) => {
            const selected = index === this.selectedIndex ? 'selected' : '';

            // Ajouter une étoile pour les recettes recommandées
            const etoile = recette.est_recommandee ? '<i class="bi bi-star-fill text-warning me-1"></i>' : '';

            // Construire les raisons de recommandation
            let raisonsHtml = '';
            if (recette.raisons && recette.raisons.length > 0) {
                raisonsHtml = `<br><small class="text-success fw-bold"><i class="bi bi-lightbulb-fill me-1"></i>${recette.raisons.join(' • ')}</small>`;
            }

            html += `
                <div class="recipe-search-item ${selected}" data-index="${index}" onclick="recipeSearchInstances['${this.input.id}'].selectRecipe(this.parentElement.children[${index}].recipeData)">
                    <div class="recipe-search-item-header">
                        <span class="recipe-search-item-name">${etoile}${recette.nom}</span>
                        <span class="badge bg-${recette.couleur_saison} recipe-search-season">${recette.icone_saison}</span>
                    </div>
                    <div class="recipe-search-item-details">
                        <small class="text-muted">
                            <i class="bi bi-people"></i> ${recette.portions}p
                            <i class="bi bi-clock ms-2"></i> ${recette.temps_total}
                            ${recette.evaluation > 0 ? `<i class="bi bi-star-fill text-warning ms-2"></i> ${recette.evaluation}/5` : ''}
                        </small>
                        <br>
                        <small class="text-muted fst-italic">${recette.mois_saison}</small>
                        ${raisonsHtml}
                    </div>
                </div>
            `;
        });

        this.resultsContainer.innerHTML = html;
        this.resultsContainer.style.display = 'block';
        this.addActiveClass();

        // Stocker les données des recettes pour l'accès au clic
        Array.from(this.resultsContainer.children).forEach((item, index) => {
            item.recipeData = this.results[index];
        });
    }

    addActiveClass() {
        // Remonter pour trouver la carte du jour entier
        let parent = this.input.closest('.card');
        if (parent) {
            parent.classList.add('recipe-search-active');
        }
    }

    removeActiveClass() {
        let parent = this.input.closest('.card');
        if (parent) {
            parent.classList.remove('recipe-search-active');
        }
    }

    updateSelection() {
        Array.from(this.resultsContainer.children).forEach((item, index) => {
            if (index === this.selectedIndex) {
                item.classList.add('selected');
                item.scrollIntoView({ block: 'nearest' });
            } else {
                item.classList.remove('selected');
            }
        });
    }

    selectRecipe(recette) {
        this.input.value = recette.nom;
        this.hiddenInput.value = recette.id;
        this.hideResults();

        // Déclencher un événement personnalisé
        this.input.dispatchEvent(new CustomEvent('recipeSelected', { detail: recette }));

        // Mettre à jour les recommandations dans tous les autres champs
        this.updateOtherSearchFields();
    }

    updateOtherSearchFields() {
        // Rafraîchir les résultats de tous les autres champs de recherche du formulaire
        const form = this.input.closest('form');
        if (!form) return;

        // Pour chaque instance de recherche dans le formulaire
        Object.values(window.recipeSearchInstances).forEach(instance => {
            // Ne pas rafraîchir le champ actuel
            if (instance !== this && instance.input.closest('form') === form) {
                // Si le champ a déjà le focus, rafraîchir immédiatement
                if (document.activeElement === instance.input) {
                    const query = instance.input.value.trim();
                    instance.search(query);
                }
            }
        });
    }

    hideResults() {
        this.resultsContainer.style.display = 'none';
        this.selectedIndex = -1;
        this.removeActiveClass();
    }

    async loadInitialRecipe() {
        try {
            const response = await fetch(`/recettes/api/search?menu_id=${this.menuId || ''}`);
            const data = await response.json();
            const recette = data.find(r => r.id === this.currentRecipeId);

            if (recette) {
                this.input.value = recette.nom;
                this.hiddenInput.value = recette.id;
            }
        } catch (error) {
            console.error('Erreur lors du chargement de la recette:', error);
        }
    }
}

// Stockage global des instances pour l'accès depuis le HTML
window.recipeSearchInstances = {};

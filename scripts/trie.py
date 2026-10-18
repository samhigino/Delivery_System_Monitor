# Nó para a Trie
class Node:
    def __init__(self, prf, isend=False, idx=-1):
        self.prefix = prf       # Prefixo da sua subárvore
        self.children = {}      # Filhos - mapeia a primeira letra de um prefixo para um nó
        self.is_end = isend     # Diz se o nó é uma folha, ou seja, armazena uma palavra inteira
        self.index = idx        # Índice da palavra que o nó armazena (-1 se is_end for Falso)

    # Adiciona um nó como filho deste nó
    def add_child(self, key, node):
        self.children[key] = node

    # Pega o prefixo de um filho usando uma chave
    def get_child_prefix(self, key):
        return self.children[key].prefix

    # Remove todos os filhos deste nó
    def clear_children(self):
        self.children.clear()

# Função auxiliar para achar o comprimento do maior prefixo comum de duas palavras
def common_prefix_length(a, b):
    l = 0
    while l < len(a) and l < len(b) and a[l] == b[l]:
        l += 1
    return l

# Trie compacta
class Trie:
    def __init__(self):
        self.root = Node("")
        self.elem = []
        self.elem_count = 0

    # Insere uma cadeia na Trie
    def insert(self, str):
        node = self.root
        i = 0

        while i < len(str):
            key = str[i]
            path_exists = key in node.children

            # Não existe nó, então precisamos criar um novo
            if not path_exists:
                self.elem.append(str)
                new_node = Node(str[i:], True, self.elem_count)
                self.elem_count += 1
                node.add_child(key, new_node)
                break

            # Existe um nó para onde podemos caminhar
            prefix = node.get_child_prefix(key)
            cpl = common_prefix_length(prefix, str[i:])

            # Prefixos diferem em algum ponto
            if cpl < len(prefix):
                # Adiciona um nó folha para a palavra
                self.elem.append(str)
                leaf_node = Node(str[(i+cpl):], True, self.elem_count)
                self.elem_count += 1

                # Adiciona um nó interno comum
                intern_node = Node(str[i:(i+cpl)])
                old_child = node.children[key]
                node.children[key] = intern_node

                # Ajusta as relações
                old_child.prefix = prefix[cpl:]
                intern_node.add_child(prefix[cpl], old_child)
                intern_node.add_child(str[i+cpl], leaf_node)

                break
                    
            # Prefixos não diferem - podemos caminhar a partir de node
            else:
                i += cpl
                node = node.children[key]
                continue
            
        return

    # Imprime a árvore - mais para debug
    def print_self(self):
        self.print_self_recursive(self.root)

    def print_self_recursive(self, src):
        print(f"\"{src.prefix}\":", src.children.keys())
        for key in src.children:
            self.print_self_recursive(src.children[key])

    # Procura uma palavra na árvore, retorna True se encontrou ou false se não encontrou
    def lookup(self, str):
        node = self.root
        i = 0
    
        while i < len(str):
            key = str[i]
            path_exists = key in node.children
    
            if not path_exists:
                return False
    
            prefix = node.get_child_prefix(key)
            cpl = common_prefix_length(prefix, str[i:])
    
            if cpl < len(prefix):
                return False
            else:
                i += cpl
                node = node.children[key]
                continue
    
        return node.is_end

    # Auxiliar para a busca por prefixo
    def get_all_subtree(self, node, lst=list, acc=str):
        for child in node.children.items():
            acc_i = acc + child[1].prefix
            if child[1].is_end:
                lst.append(acc_i)
            lst = lst + self.get_all_subtree(child[1], [], acc_i)
        return lst

    # Realiza uma busca por prefixo para encontrar vários itens
    def search_many(self, pref):
        node = self.root
        i = 0
        words_found = []
        cpl = 0

        # Acha o primeiro nó que contém todo o prefixo str
        while i < len(pref):
            key = pref[i]
            path_exists = key in node.children
        
            if not path_exists:
                return words_found

            node = node.children[key]
            prefix = node.prefix
            cpl = common_prefix_length(prefix, pref[i:])
        
            if cpl < len(prefix):
                break
            else:
                i += cpl
                continue

        acc = pref + node.prefix[cpl:]
        if node.is_end:
            words_found.append(acc)
        words_found = words_found + self.get_all_subtree(node, words_found, acc)

        return words_found

    # Funções para imprimir a árvore (mais para debug)
    def print_self(self):
        self.print_self_recursive(self.root)
    
    def print_self_recursive(self, src):
        print(f"\"{src.prefix}\":", src.children.keys())
        for key in src.children:
            self.print_self_recursive(src.children[key])

    # Limpa a árvore
    def clear(self, str):
        self.root.clear_children()
        self.elem.clear()
        self.elem_count = 0
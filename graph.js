function drawGraph(destination) {
        
            var source='0xe1f3294e25bb72a2fb53addb82aa1a033797e6e3';
            // var destination='0xfef4c8d00521696871857c12a098f86c6bc5340e';

            var graph = new Graph(new vis.DataSet([]),
                new vis.DataSet([
                    {
                        'id': source,
                        'label': 'SOURCE:'+source.substring(0,10)+'...',
                        'group': 'source',
                        'title': source,
                        'link': '',
						x: 0,
						y: 200
                    },
                    {
                        'id': destination,
                        'label': 'DESTINATION:'+destination.substring(0,10)+'...',
                        'group': 'destination',
                        'title': destination,
                        'link': '',
						x: 500,
						y: 200
                    }
				]), '/graph'
			);

            graph.draw();

            setTimeout(function(){
                graph.expand(graph.nodes.getIds()[0]);
            }, 800);

            setTimeout(function(){
                graph.expand(graph.nodes.getIds()[1]);
			}, 1600);
        };

        function Graph(edges, nodes, expand_path){

            this.edges = edges;
            this.nodes = nodes;
            this.expand_path = expand_path;

            this.display_edges = {
                select_transfers: true, select_calls: true, select_references: false
            };

            this.options = {
                physics: {
                    stabilization: {
                        enabled: false,
                        iterations: 10,
                        onlyDynamicEdges: true
                    },
                    barnesHut: {
                        damping: 0.4,
                        avoidOverlap: 0.1,
                        springConstant: 0.17
                    }
                },
                groups: {
                    smart_contract: {
                        shape: 'icon',
                        icon: {
                            face: 'Glyphicons Halflings',
                            code: '\ue019',
                            size: 50,
                            color: '#f0a30a'
                        }
                    },
                    destination: {
                        shape: 'icon',
                        icon: {
                            face: 'Glyphicons Halflings',
                            code: '\ue225',
                            size: 90,
                            color: '#03a9f4'
                        }
                    },
                    source: {
                        shape: 'icon',
                        icon: {
                            face: 'Glyphicons Halflings',
                            code: '\ue008',
                            size: 60,
                            color: '#009688'
                        }
                    },
                    address: {
                        shape: 'icon',
                        icon: {
                            face: 'Glyphicons Halflings',
                            code: '\ue008',
                            size: 20,
                            color: '#009688'
                        }
                    },
                    token: {
                        shape: 'icon',
                        icon: {
                            face: 'Glyphicons Halflings',
                            code: '\ue201',
                            size: 70,
                            color: '#ff5722'
                        }
                    }
                }
            };

            this.container = document.getElementById('address_graph');

            this.draw = function(){
                var g = this;
                var network = new vis.Network(this.container, this, this.options);

                network.on('dragEnd', function (t) {
                    for(var i=0;i<t.nodes.length;i++){
                        g.nodes.update({id: t.nodes[i], physics: false});
                    }
                });

                network.on('doubleClick', function(target){
                    if(target.nodes.length>0){
                        var node_id = target.nodes[0];
                        if(g.nodes.get(node_id).group!='system'){
                            g.expand(node_id);
                        }

                    }
                });

                network.on("oncontext", function (params) {
                    if (params.nodes.length === 1) {
                        var node = g.nodes.get(params.nodes[0]);
                        window.open(node.link, '_blank');
                    }
                });

                this.network = network;
            };


            this.freeze = function(){
                var g = this;
                g.nodes.forEach(function(node){
                    if(node.physics!==false){
                        g.nodes.update({id: node.id, physics: false});
                    }

                });
            };

            this.expand = function(node_address){
                if(!this.expand_path)
                    return;
                $('#graph_status .alert').hide();
                $('#graph_status .status-progress').show().text('Expanding '+node_address+'...');
                var g = this;
                $.ajax(this.expand_path, {
                    data: {
                        destination_address: node_address
                    },
                    dataType: 'json'
                }).done(function( data ) {
                    g.freeze();
                    g.process(node_address, data);
                    $('#graph_status .alert').hide();
                    $('#graph_status .status-info').show().text('Done!');
                }).fail(function( x, y, error) {
                    $('#graph_status .alert').hide();
                    $('#graph_status .status-error').show().text('Failed '+node_address);
                });
            };

            this.load_tx_data = function(tx_hash, request_url){

                $('#graph_status .alert').hide();
                $('#graph_status .status-progress').show().text('Loading '+tx_hash+'...');
                var g = this;
                $.ajax(request_url, {
                    dataType: 'json',
                }).done(function( data ) {
                    g.process_all_nodes(data);
                    g.draw();
                    $('#graph_status .alert').hide();
                    $('#graph_status .status-info').show().text('Done');
                }).fail(function( x, y, error) {
                    $('#graph_status .alert').hide();
                    $('#graph_status .status-error').show().text('Error '+tx_hash);
                });

            };

            this.process_all_nodes = function(data){

                for(var i=0; i<data.length;i++){

                    var d = data[i];
                    var from_node = this.nodes.get(d[0].id);
                    if(!from_node){
                        from_node = d[0];
                        this.nodes.add(from_node);
                    }

                    var to_node = this.nodes.get(d[1].id);
                    if(!to_node){
                        to_node = d[1];
                        this.nodes.add(to_node);
                    }

                    var new_edge = this.edge(from_node.id, [to_node, d[2], d[3], d[5], d[6], 1, d[7]]);
                    if(!this.edges.get(new_edge.id)){
                        this.edges.add(new_edge);
                    }
                }

            };

            this.process = function(node_address, data){

                for(var i=0;i<data.length;i++){
                    var d = data[i];
                    var node = this.nodes.get(data[i][0].id);

                    if(!node){
                        this.nodes.add(data[i][0]);
                    }

                    var new_edge = this.edge(node_address, data[i]);
                    if(!this.edges.get(new_edge.id)){
                        this.edges.add(new_edge);
                    }

                }


            };

            this.edge = function(node_address, data){
                var e = this.nodeData(node_address, data, data[0]);
                e['id'] = this.hashCode([e.select_type, e.from, e.to, e.label]);
                return e;
            };

            this.nodeData = function(node_address, data, node){

                var width, currency_name;

                var width_counts = Math.log(data[5])+1;

                if(data[6]==1){
                    width = (data[4] > 1) ? Math.log(data[4])+1 : 1
                    currency_name = '<b>Ether</b>';
                }else{
                    width = width_counts;
                    currency_name = data[3];
                }

                var value = parseFloat(data[4])<=1e-6 ? data[4] : numeral(data[4]).format('0.0000a')


                switch(data[1]){
                    case 'transfer_from':
                        return {
                            from: node.id,
                            to: node_address,
                            arrows: 'to',
                            label: value + ' ' + currency_name,
                            color: {color: 'grey', highlight: '#ff5722'},
                            font: {align: 'middle', multi: true},
                            smooth: true,
                            width: width,
                            select_type: 'select_transfers',
                            hidden: !this.display_edges['select_transfers']
                        };
                    case 'transfer_to':
                        return {
                            from: node_address,
                            to: node.id,
                            arrows: 'to',
                            label: value + ' ' + currency_name,
                            color:  {color: 'grey', highlight: '#ff5722'},
                            font: {align: 'middle', multi: true},
                            smooth: true,
                            width: width,
                            select_type: 'select_transfers',
                            hidden: !this.display_edges['select_transfers']
                        };

                }
            };

            this.hashCode = function(data){

                var string = JSON.stringify(data);
                if (Array.prototype.reduce){
                    return string.split("").reduce(function(a,b){a=((a<<5)-a)+b.charCodeAt(0);return a&a},0);
                }
                var hash = 0;
                if (string.length === 0) return hash;
                for (var i = 0; i < string.length; i++) {
                    var character  = string.charCodeAt(i);
                    hash  = ((hash<<5)-hash)+character;
                    hash = hash & hash; // Convert to 32bit integer
                }
                return hash;
            };

            this.update_selector = function(selector_id, selector_checked){
                var g = this;
                g.display_edges[selector_id] = selector_checked;
                g.edges.forEach(function(edge){
                    if(edge.select_type==selector_id){
                        g.edges.update({id: edge.id, hidden: !selector_checked});
                    }

                });
            };

        }

        $('#fullscreen').click(function(){
            $('#graph_window').toggleClass('fullscreen');

            if($('.navbar').is(":visible")){
                $('.navbar').hide();
                $('.container > *').hide();
                $('#graph_window').show();

                $('#fullscreen .enter-fs').hide();
                $('#fullscreen .exit-fs').show();

            }else{
                $('.navbar').show();
                $('.container > *').show();

                $('#fullscreen .enter-fs').show();
                $('#fullscreen .exit-fs').hide();

            }
        });
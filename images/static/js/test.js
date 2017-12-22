$.getJSON('http://flickr.com/api/test.json', function(data) {
    alert(data);
});

//do wszystkich elementów a z klasą like
        $('a.like').click(function(e){
            // zapobiegnięcie domyślnemu zachowaniu się elementu likna
            e.preventDefault();
            $.post('{% url "images:like" %}',
                {
                    //podczas kliknięcia zostają pobrane te argumenty elementu <a>
                    id: $(this).data('id'),
                    action: $(this).data('action')
                },
                function(data) {
                    if (data['status'] == 'ok') {
                        var previous_action = $('a.like').data('action');
                        // Zmiana wartości atrybutu data-action.
                        $('a.like').data('action', previous_action == 'like' ? 'unlike' : 'like');
                        // Zmiana tekstu wyświetlanego przez łącze.
                        $('a.like').text(previous_action == 'like' ? 'Nie lubię' : 'Lubię');
                        // Uaktualnienie całkowitej liczby polubienia danego obrazu.
                        var previous_likes = parseInt($('span.count .total').text());
                        $('span.count .total').text(previous_action == 'like' ? previous_likes + 1 : previous_likes - 1);
                        if ($('span.count .total').val() == 0) {
                            $('#$zero_likes_case').hide();
                        }
                    }
                });
        });
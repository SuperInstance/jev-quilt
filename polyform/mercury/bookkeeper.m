% bookkeeper.m — law 4 as a logic program.
% STATUS: UNVERIFIED (no mmc on this node). Syntax follows Mercury
% reference conventions; the hash is a LABELED PLACEHOLDER until the
% fleet's fnv1a port lands. Trust nothing here until mmc says it.
%
% The book is not a log file. It is a theorem: every state change of a
% cell has exactly one receipt, and the receipts chain.

:- module bookkeeper.
:- interface.
:- import_module list, int, string.

:- type receipt --->
    receipt(
        tick    :: int,
        prev    :: int,     % chain value before this receipt
        kind    :: string,  % "decided" | "rejected" | "refused" | "booked"
        fp      :: int,     % state fingerprint
        chain   :: int      % fnv1a(prev, payload_hash)
    ).

    % book(OldChain, Kind, Fingerprint, Receipt, NewChain).
:- pred book(int::in, string::in, int::in, receipt::out, int::out) is det.

    % chain_valid(Receipts, InitialChain). True iff the log replays.
:- pred chain_valid(list(receipt)::in, int::in) is semidet.

    % wake_state(Receipts, Ticks, HeadChain).
:- pred wake_state(list(receipt)::in, int::out, int::out) is det.

:- implementation.
:- import_module require.

book(Prev, Kind, Fp, R, Chain) :-
    % PLACEHOLDER hash — replace with fleet fnv1a port before trusting.
    hash_payload(Prev, Kind, Fp, Payload),
    Chain = Payload,
    R = receipt(1, Prev, Kind, Fp, Chain).

:- pred hash_payload(int::in, string::in, int::in, int::out) is det.
hash_payload(Prev, Kind, Fp, Out) :-
    % honest stand-in: order-mixing without crypto pretension
    string.length(Kind, L),
    Out = (Prev * 31 + Fp * 17 + L) mod 18446744073709551557.

chain_valid([], _).
chain_valid([R | Rs], Prev) :-
    R ^ prev = Prev,
    hash_payload(Prev, R ^ kind, R ^ fp, Expect),
    R ^ chain = Expect,
    chain_valid(Rs, R ^ chain).

wake_state(Rs, length(Rs), Head) :-
    ( Rs = [] -> Head = 0
    ; Rs = [R | _] -> Head = R ^ chain  % last cons; Mercury lists snoc here
    ).
